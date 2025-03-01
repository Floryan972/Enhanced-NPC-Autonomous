#include "main.h"
#include "script.h"
#include "npc_controller.h"
#include <windows.h>

BOOL APIENTRY DllMain(HMODULE hModule, DWORD reason, LPVOID lpReserved)
{
    switch (reason)
    {
        case DLL_PROCESS_ATTACH:
            scriptRegister(hModule, ScriptMain);
            break;

        case DLL_PROCESS_DETACH:
            scriptUnregister(hModule);
            break;
    }
    return TRUE;
}
