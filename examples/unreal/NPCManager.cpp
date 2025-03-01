#include "NPCManager.h"
#include "NPC.h"
#include "BehaviorTree/BlackboardComponent.h"
#include "BehaviorTree/BehaviorTreeComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Animation/AnimMontage.h"
#include "Engine/World.h"

ANPCManager::ANPCManager()
{
    PrimaryActorTick.bCanEverTick = true;
    LastUpdateTime = 0.0f;
}

void ANPCManager::BeginPlay()
{
    Super::BeginPlay();
    InitializeNPCs();
}

void ANPCManager::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    Super::EndPlay(EndPlayReason);
    NPCActors.Empty();
}

void ANPCManager::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // Mise à jour périodique
    if (GetWorld()->GetTimeSeconds() - LastUpdateTime >= UpdateInterval)
    {
        LastUpdateTime = GetWorld()->GetTimeSeconds();
        UpdateNPCs();
    }
}

void ANPCManager::InitializeNPCs()
{
    // Récupération de l'état du monde
    TSharedPtr<FJsonObject> RequestData = MakeShared<FJsonObject>();
    SendHttpRequest(TEXT("world"), TEXT("GET"), RequestData,
        FHttpRequestCompleteDelegate::CreateUObject(this, &ANPCManager::OnWorldStateReceived));
}

void ANPCManager::OnWorldStateReceived(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess)
{
    if (!bSuccess || !Response.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to receive world state"));
        return;
    }

    TSharedPtr<FJsonObject> JsonObject;
    if (!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Response->GetContentAsString()),
        JsonObject))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to parse world state"));
        return;
    }

    // Création des PNJ
    const TArray<TSharedPtr<FJsonValue>>* NPCsArray;
    if (JsonObject->TryGetArrayField(TEXT("npcs"), NPCsArray))
    {
        for (const auto& NPCValue : *NPCsArray)
        {
            const TSharedPtr<FJsonObject>& NPCObject = NPCValue->AsObject();
            const FString NPCId = NPCObject->GetStringField(TEXT("id"));
            CreateNPC(NPCId, NPCObject);
        }
    }
}

void ANPCManager::CreateNPC(const FString& NPCId, const TSharedPtr<FJsonObject>& NPCData)
{
    // Chargement du blueprint
    FString BlueprintPath = NPCData->GetStringField(TEXT("blueprint_path"));
    UClass* NPCClass = LoadClass<ANPC>(nullptr, *BlueprintPath);
    if (!NPCClass)
    {
        NPCClass = ANPC::StaticClass();
    }

    // Création de l'acteur
    FVector Location = FVector::ZeroVector;
    FRotator Rotation = FRotator::ZeroRotator;
    if (const TSharedPtr<FJsonObject>* PositionObject;
        NPCData->TryGetObjectField(TEXT("position"), PositionObject))
    {
        Location.X = (*PositionObject)->GetNumberField(TEXT("x"));
        Location.Y = (*PositionObject)->GetNumberField(TEXT("y"));
        Location.Z = (*PositionObject)->GetNumberField(TEXT("z"));
    }

    FActorSpawnParameters SpawnParams;
    SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;

    ANPC* NPCActor = GetWorld()->SpawnActor<ANPC>(NPCClass, Location, Rotation, SpawnParams);
    if (NPCActor)
    {
        NPCActor->Initialize(NPCId, NPCData);
        NPCActors.Add(NPCId, NPCActor);

        if (bShowDebugLogs)
        {
            UE_LOG(LogTemp, Log, TEXT("Created NPC: %s"), *NPCId);
        }
    }
}

void ANPCManager::UpdateNPCs()
{
    // Préparation des données
    TSharedPtr<FJsonObject> UpdateData = MakeShared<FJsonObject>();
    UpdateData->SetObjectField(TEXT("npc_positions"), GetNPCPositions());
    UpdateData->SetObjectField(TEXT("npc_animations"), GetNPCAnimations());
    UpdateData->SetNumberField(TEXT("delta_time"), GetWorld()->GetDeltaSeconds());

    // Envoi de la mise à jour
    SendHttpRequest(TEXT("unreal/update"), TEXT("POST"), UpdateData,
        FHttpRequestCompleteDelegate::CreateUObject(this, &ANPCManager::OnUpdateResponse));
}

TSharedPtr<FJsonObject> ANPCManager::GetNPCPositions()
{
    TSharedPtr<FJsonObject> Positions = MakeShared<FJsonObject>();

    for (const auto& NPCPair : NPCActors)
    {
        if (NPCPair.Value && !NPCPair.Value->IsPendingKill())
        {
            TSharedPtr<FJsonObject> Position = MakeShared<FJsonObject>();
            FVector Loc = NPCPair.Value->GetActorLocation();
            Position->SetNumberField(TEXT("x"), Loc.X);
            Position->SetNumberField(TEXT("y"), Loc.Y);
            Position->SetNumberField(TEXT("z"), Loc.Z);
            Positions->SetObjectField(NPCPair.Key, Position);
        }
    }

    return Positions;
}

TSharedPtr<FJsonObject> ANPCManager::GetNPCAnimations()
{
    TSharedPtr<FJsonObject> Animations = MakeShared<FJsonObject>();

    for (const auto& NPCPair : NPCActors)
    {
        if (NPCPair.Value && !NPCPair.Value->IsPendingKill())
        {
            Animations->SetStringField(NPCPair.Key, NPCPair.Value->GetCurrentAnimation());
        }
    }

    return Animations;
}

void ANPCManager::OnUpdateResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess)
{
    if (!bSuccess || !Response.IsValid())
        return;

    TSharedPtr<FJsonObject> JsonObject;
    if (FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Response->GetContentAsString()),
        JsonObject))
    {
        ProcessNPCUpdates(JsonObject);
    }
}

void ANPCManager::ProcessNPCUpdates(const TSharedPtr<FJsonObject>& Response)
{
    const TSharedPtr<FJsonObject>* Updates;
    if (!Response->TryGetObjectField(TEXT("npc_updates"), Updates))
        return;

    for (const auto& UpdatePair : (*Updates)->Values)
    {
        const FString& NPCId = UpdatePair.Key;
        if (ANPC* NPCActor = NPCActors.FindRef(NPCId))
        {
            FNPCUpdate Update;
            const TSharedPtr<FJsonObject>& UpdateObject = UpdatePair.Value->AsObject();

            Update.BehaviorTreeState = UpdateObject->GetStringField(TEXT("behavior_tree_state"));
            
            const TSharedPtr<FJsonObject>* BlackboardObject;
            if (UpdateObject->TryGetObjectField(TEXT("blackboard_values"), BlackboardObject))
            {
                for (const auto& BlackboardPair : (*BlackboardObject)->Values)
                {
                    Update.BlackboardValues.Add(BlackboardPair.Key,
                        BlackboardPair.Value->AsString());
                }
            }

            Update.AnimationMontage = UpdateObject->GetStringField(TEXT("animation_montage"));

            NPCActor->ApplyUpdate(Update);
        }
    }
}

void ANPCManager::SendHttpRequest(const FString& Endpoint, const FString& Verb,
    const TSharedPtr<FJsonObject>& Data, const FHttpRequestCompleteDelegate& Callback)
{
    FString Url = ApiUrl + TEXT("/") + Endpoint;
    TSharedRef<IHttpRequest, ESPMode::ThreadSafe> HttpRequest = FHttpModule::Get().CreateRequest();
    
    HttpRequest->SetURL(Url);
    HttpRequest->SetVerb(Verb);
    HttpRequest->SetHeader(TEXT("Content-Type"), TEXT("application/json"));

    if (Data.IsValid())
    {
        FString JsonString;
        TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&JsonString);
        FJsonSerializer::Serialize(Data.ToSharedRef(), Writer);
        HttpRequest->SetContentAsString(JsonString);
    }

    HttpRequest->OnProcessRequestComplete() = Callback;
    HttpRequest->ProcessRequest();
}

void ANPCManager::InteractWithNPC(const FString& NPCId, const FString& Action,
    const TMap<FString, FString>& Data)
{
    TSharedPtr<FJsonObject> RequestData = MakeShared<FJsonObject>();
    RequestData->SetStringField(TEXT("npc_id"), NPCId);
    RequestData->SetStringField(TEXT("action"), Action);

    TSharedPtr<FJsonObject> DataObject = MakeShared<FJsonObject>();
    for (const auto& DataPair : Data)
    {
        DataObject->SetStringField(DataPair.Key, DataPair.Value);
    }
    RequestData->SetObjectField(TEXT("data"), DataObject);

    SendHttpRequest(TEXT("interact"), TEXT("POST"), RequestData,
        FHttpRequestCompleteDelegate::CreateLambda([this](FHttpRequestPtr Request,
            FHttpResponsePtr Response, bool bSuccess)
        {
            if (bSuccess && Response.IsValid())
            {
                if (bShowDebugLogs)
                {
                    UE_LOG(LogTemp, Log, TEXT("Interaction successful"));
                }
            }
        }));
}

ANPC* ANPCManager::GetNPCActor(const FString& NPCId) const
{
    return NPCActors.FindRef(NPCId);
}
