#pragma once

void ScriptMain();
void ScriptInit();

// Structure pour les coordonnées 3D
struct Vector3 {
    float x;
    float y;
    float z;
};

// Fonctions utilitaires
inline float GetDistance(Vector3 a, Vector3 b) {
    return sqrt(
        (a.x - b.x) * (a.x - b.x) +
        (a.y - b.y) * (a.y - b.y) +
        (a.z - b.z) * (a.z - b.z)
    );
}
