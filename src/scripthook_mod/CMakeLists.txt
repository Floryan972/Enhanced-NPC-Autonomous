cmake_minimum_required(VERSION 3.10)
project(EnhancedNPCMod)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Définir le chemin vers le SDK ScriptHook
set(SCRIPTHOOK_SDK_PATH "${CMAKE_SOURCE_DIR}/vendor/ScriptHookV_SDK")

# Sources du projet
set(SOURCE_FILES
    main.cpp
    script.cpp
    npc_controller.cpp
)

# Headers du projet
set(HEADER_FILES
    script.h
    npc_controller.h
)

# Créer la DLL
add_library(EnhancedNPCMod SHARED
    ${SOURCE_FILES}
    ${HEADER_FILES}
)

# Inclure les headers du SDK
target_include_directories(EnhancedNPCMod PRIVATE
    ${SCRIPTHOOK_SDK_PATH}/inc
)

# Lier avec ScriptHookV
target_link_libraries(EnhancedNPCMod
    ${SCRIPTHOOK_SDK_PATH}/lib/ScriptHookV.lib
)
