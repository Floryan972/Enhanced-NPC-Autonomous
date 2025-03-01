#include "routine_system.h"
#include "natives.h"
#include "personality_system.h"
#include <random>

void RoutineSystem::initializeRoutine(Ped ped) {
    DailyRoutine routine;
    routine.currentActivityIndex = 0;
    routine.isActive = true;
    
    // Obtenir la position actuelle comme position de départ
    routine.homeLocation = ENTITY::GET_ENTITY_COORDS(ped, true);
    
    // Générer une routine aléatoire
    generateRandomRoutine(routine);
    
    pedRoutines[ped] = routine;
}

void RoutineSystem::generateRandomRoutine(DailyRoutine& routine) {
    // Activités de base
    std::vector<std::string> basicActivities = {
        "SLEEP",
        "WORK",
        "EAT",
        "LEISURE",
        "SHOPPING",
        "EXERCISE"
    };

    // Générer des activités pour une journée complète
    for (int hour = 0; hour < 24; hour += 3) {
        RoutineActivity activity;
        activity.timeSlot.startHour = hour;
        activity.timeSlot.endHour = hour + 3;

        // Choisir une activité en fonction de l'heure
        if (hour >= 22 || hour < 6) {
            activity.name = "SLEEP";
            activity.location = routine.homeLocation;
            activity.animation = "WORLD_HUMAN_SLEEP_GROUND";
        }
        else if (hour >= 9 && hour < 17) {
            activity.name = "WORK";
            activity.location = routine.workLocation;
            activity.animation = "WORLD_HUMAN_CLIPBOARD";
        }
        else {
            // Activité aléatoire pour les autres moments
            int randomIndex = rand() % basicActivities.size();
            activity.name = basicActivities[randomIndex];
            activity.location = findNearestLocationForActivity(activity.name, routine.homeLocation);
            
            // Définir l'animation appropriée
            if (activity.name == "EAT")
                activity.animation = "WORLD_HUMAN_SEAT_WALL_EATING";
            else if (activity.name == "LEISURE")
                activity.animation = "WORLD_HUMAN_STAND_MOBILE";
            else if (activity.name == "SHOPPING")
                activity.animation = "WORLD_HUMAN_STAND_IMPATIENT";
            else if (activity.name == "EXERCISE")
                activity.animation = "WORLD_HUMAN_JOG_STANDING";
        }

        activity.duration = 180.0f; // 3 heures en minutes
        activity.isOptional = (activity.name != "SLEEP" && activity.name != "WORK");
        
        routine.activities.push_back(activity);
    }
}

void RoutineSystem::updateRoutines() {
    for (auto& [ped, routine] : pedRoutines) {
        if (!routine.isActive || routine.activities.empty()) continue;
        if (!ENTITY::DOES_ENTITY_EXIST(ped)) continue;

        // Obtenir l'activité actuelle
        RoutineActivity& currentActivity = routine.activities[routine.currentActivityIndex];
        
        // Vérifier si c'est l'heure de cette activité
        if (isTimeForActivity(currentActivity.timeSlot)) {
            executeActivity(ped, currentActivity);
        } else {
            // Passer à l'activité suivante
            routine.currentActivityIndex = (routine.currentActivityIndex + 1) % routine.activities.size();
        }
    }
}

bool RoutineSystem::isTimeForActivity(const TimeSlot& timeSlot) {
    int currentHour = TIME::GET_CLOCK_HOURS();
    return currentHour >= timeSlot.startHour && currentHour < timeSlot.endHour;
}

void RoutineSystem::executeActivity(Ped ped, const RoutineActivity& activity) {
    // Vérifier si le PED est déjà en train de faire l'activité
    if (AI::GET_SCRIPT_TASK_STATUS(ped, 0x93375924) == 1) return;

    // Vérifier la distance à la destination
    Vector3 currentPos = ENTITY::GET_ENTITY_COORDS(ped, true);
    float distance = SYSTEM::VDIST(
        currentPos.x, currentPos.y, currentPos.z,
        activity.location.x, activity.location.y, activity.location.z
    );

    if (distance > 3.0f) {
        // Se déplacer vers la destination
        AI::TASK_GO_TO_COORD_ANY_MEANS(
            ped,
            activity.location.x,
            activity.location.y,
            activity.location.z,
            2.0f, 0, 0, 786603, 0xbf800000
        );
    } else {
        // Exécuter l'animation de l'activité
        AI::TASK_START_SCENARIO_IN_PLACE(ped, activity.animation.c_str(), 0, true);
    }
}

Vector3 RoutineSystem::findNearestLocationForActivity(const std::string& activityName, const Vector3& currentPos) {
    // Simuler la recherche d'un point d'intérêt approprié
    float radius = 100.0f;
    Vector3 location = currentPos;
    
    // Ajouter un décalage aléatoire
    location.x += (float)(rand() % (int)radius) - radius/2;
    location.y += (float)(rand() % (int)radius) - radius/2;
    
    // Obtenir la hauteur du sol
    float groundZ;
    if (MISC::GET_GROUND_Z_FOR_3D_COORD(location.x, location.y, location.z + 100.0f, &groundZ, 0)) {
        location.z = groundZ;
    }
    
    return location;
}

void RoutineSystem::setHomeLocation(Ped ped, const Vector3& location) {
    auto it = pedRoutines.find(ped);
    if (it != pedRoutines.end()) {
        it->second.homeLocation = location;
    }
}

void RoutineSystem::setWorkLocation(Ped ped, const Vector3& location) {
    auto it = pedRoutines.find(ped);
    if (it != pedRoutines.end()) {
        it->second.workLocation = location;
    }
}

void RoutineSystem::interruptRoutine(Ped ped) {
    auto it = pedRoutines.find(ped);
    if (it != pedRoutines.end()) {
        it->second.isActive = false;
        AI::CLEAR_PED_TASKS(ped);
    }
}

void RoutineSystem::resumeRoutine(Ped ped) {
    auto it = pedRoutines.find(ped);
    if (it != pedRoutines.end()) {
        it->second.isActive = true;
    }
}
