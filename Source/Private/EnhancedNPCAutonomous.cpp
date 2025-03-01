#include "EnhancedNPCAutonomous.h"
#include "PythonScriptPlugin.h"
#include "IPythonScriptPlugin.h"

#define LOCTEXT_NAMESPACE "FEnhancedNPCAutonomousModule"

void FEnhancedNPCAutonomousModule::StartupModule()
{
    // Chemin vers notre script Python
    FString PythonScriptPath = FPaths::Combine(
        FPaths::ProjectPluginsDir(),
        TEXT("EnhancedNPCAutonomous"),
        TEXT("Content"),
        TEXT("Python"),
        TEXT("plugin_init.py")
    );

    // Vérifie si le plugin Python est disponible
    if (IPythonScriptPlugin::IsAvailable())
    {
        // Exécute notre script Python
        IPythonScriptPlugin::Get()->ExecPythonCommand(*FString::Printf(
            TEXT("import sys; sys.path.append('%s'); import plugin_init; plugin_init.initialize()"),
            *FPaths::GetPath(PythonScriptPath)
        ));
    }
}

void FEnhancedNPCAutonomousModule::ShutdownModule()
{
}

#undef LOCTEXT_NAMESPACE
	
IMPLEMENT_MODULE(FEnhancedNPCAutonomousModule, EnhancedNPCAutonomous)
