#pragma once
#include "types.h"
#include <vector>
#include <string>
#include <unordered_map>

struct TimeSlot {
    int startHour;
    int endHour;
};

struct RoutineActivity {
    std::string name;
    Vector3 location;
    TimeSlot timeSlot;
    std::string animation;
    float duration;
    bool isOptional;
};

class RoutineSystem {
public:
    static RoutineSystem& getInstance() {
        static RoutineSystem instance;
        return instance;
    }

    struct DailyRoutine {
        std::vector<RoutineActivity> activities;
        int currentActivityIndex;
        bool isActive;
        Vector3 homeLocation;
        Vector3 workLocation;
    };

    void initializeRoutine(Ped ped);
    void updateRoutines();
    void setHomeLocation(Ped ped, const Vector3& location);
    void setWorkLocation(Ped ped, const Vector3& location);
    void addActivity(Ped ped, const RoutineActivity& activity);
    void interruptRoutine(Ped ped);
    void resumeRoutine(Ped ped);

private:
    RoutineSystem() {}
    std::unordered_map<Ped, DailyRoutine> pedRoutines;
    
    void generateRandomRoutine(DailyRoutine& routine);
    bool isTimeForActivity(const TimeSlot& timeSlot);
    void executeActivity(Ped ped, const RoutineActivity& activity);
    Vector3 findNearestLocationForActivity(const std::string& activityName, const Vector3& currentPos);
};
