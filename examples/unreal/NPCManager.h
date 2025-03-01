#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Http.h"
#include "Json.h"
#include "JsonUtilities.h"
#include "NPCManager.generated.h"

USTRUCT(BlueprintType)
struct FNPCUpdate
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "NPC")
    FString BehaviorTreeState;

    UPROPERTY(BlueprintReadWrite, Category = "NPC")
    TMap<FString, FString> BlackboardValues;

    UPROPERTY(BlueprintReadWrite, Category = "NPC")
    FString AnimationMontage;
};

UCLASS()
class ENHANCEDNPC_API ANPCManager : public AActor
{
    GENERATED_BODY()

public:
    ANPCManager();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(EditDefaultsOnly, Category = "Configuration")
    FString ApiUrl = TEXT("http://localhost:8000");

    UPROPERTY(EditDefaultsOnly, Category = "Configuration")
    float UpdateInterval = 0.1f;

    UPROPERTY(EditDefaultsOnly, Category = "Debug")
    bool bShowDebugLogs = false;

private:
    // Stockage des PNJ
    TMap<FString, class ANPC*> NPCActors;
    float LastUpdateTime;

    // Fonctions d'initialisation
    void InitializeNPCs();
    void CreateNPC(const FString& NPCId, const TSharedPtr<FJsonObject>& NPCData);

    // Fonctions de mise à jour
    void UpdateNPCs();
    void ProcessNPCUpdates(const TSharedPtr<FJsonObject>& Response);

    // Fonctions réseau
    void SendHttpRequest(const FString& Endpoint, const FString& Verb, 
                        const TSharedPtr<FJsonObject>& Data,
                        const FHttpRequestCompleteDelegate& Callback);
    void OnWorldStateReceived(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess);
    void OnNPCDataReceived(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess);
    void OnUpdateResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess);

    // Utilitaires
    TSharedPtr<FJsonObject> GetNPCPositions();
    TSharedPtr<FJsonObject> GetNPCAnimations();

public:
    // Interface Blueprint
    UFUNCTION(BlueprintCallable, Category = "NPC")
    void InteractWithNPC(const FString& NPCId, const FString& Action, 
                        const TMap<FString, FString>& Data);

    // Getters
    UFUNCTION(BlueprintPure, Category = "NPC")
    ANPC* GetNPCActor(const FString& NPCId) const;
};

// Classe de base pour les PNJ
UCLASS()
class ENHANCEDNPC_API ANPC : public ACharacter
{
    GENERATED_BODY()

public:
    ANPC();

    // Initialisation
    void Initialize(const FString& InNPCId, const TSharedPtr<FJsonObject>& InNPCData);

    // Mise à jour
    void ApplyUpdate(const FNPCUpdate& Update);

    // Getters
    FString GetCurrentAnimation() const { return CurrentAnimation; }
    FString GetNPCId() const { return NPCId; }

protected:
    UPROPERTY()
    FString NPCId;

    UPROPERTY()
    FString CurrentAnimation;

    UPROPERTY()
    class UBehaviorTreeComponent* BehaviorTreeComponent;

    UPROPERTY()
    class UBlackboardComponent* BlackboardComponent;

private:
    void ApplyInitialState(const TSharedPtr<FJsonObject>& NPCData);
    void UpdateBehaviorTree(const FString& State);
    void UpdateBlackboard(const TMap<FString, FString>& Values);
    void PlayAnimationMontage(const FString& MontageName);
};
