using UnityEngine;
using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using Newtonsoft.Json;
using UnityEngine.Networking;
using System.Text;

[Serializable]
public class NPCUpdate
{
    public Vector3 target_position;
    public string desired_animation;
    public Dictionary<string, object> dialogue_state;
}

[Serializable]
public class APIResponse<T>
{
    public bool success;
    public string error;
    public T data;
}

public class NPCManager : MonoBehaviour
{
    [Header("Configuration")]
    [SerializeField] private string apiUrl = "http://localhost:8000";
    [SerializeField] private float updateInterval = 0.1f;
    
    [Header("Loading Screen")]
    [SerializeField] private LoadingScreen loadingScreen;
    [SerializeField] private LoadingScreenConfig loadingConfig;
    
    [Header("Debug")]
    [SerializeField] private bool showDebugLogs = false;
    
    private Dictionary<string, GameObject> npcObjects = new Dictionary<string, GameObject>();
    private Dictionary<string, NPCController> npcControllers = new Dictionary<string, NPCController>();
    private float lastUpdateTime;
    private int totalInitSteps = 5;  // Nombre total d'étapes d'initialisation
    private int currentInitStep = 0;
    
    private void Start()
    {
        // Création de l'écran de chargement s'il n'existe pas
        if (loadingScreen == null)
        {
            var loadingPrefab = Resources.Load<GameObject>("Prefabs/LoadingScreen");
            if (loadingPrefab != null)
            {
                var loadingObj = Instantiate(loadingPrefab);
                loadingScreen = loadingObj.GetComponent<LoadingScreen>();
                
                // Application de la configuration
                if (loadingConfig != null)
                {
                    loadingScreen.ApplyConfig(loadingConfig);
                }
            }
        }
        
        // Initialisation des PNJ
        InitializeNPCs();
    }
    
    private async void InitializeNPCs()
    {
        try {
            UpdateLoadingProgress("Connecting to AI system...");
            
            // Récupération de l'état du monde
            var worldState = await GetWorldState();
            UpdateLoadingProgress("World state received");
            
            // Chargement des ressources
            UpdateLoadingProgress("Loading resources...");
            await LoadNPCResources();
            
            // Création des PNJ
            var npcs = worldState.npcs as IEnumerable<object>;
            if (npcs != null)
            {
                int npcCount = 0;
                foreach (var npc in npcs)
                {
                    string npcId = npc.ToString();
                    await CreateNPC(npcId);
                    npcCount++;
                    
                    float progress = (float)npcCount / npcs.Count();
                    UpdateLoadingProgress($"Creating NPC {npcCount}/{npcs.Count()}", 0.6f + progress * 0.3f);
                }
            }
            
            // Finalisation
            UpdateLoadingProgress("Finalizing...", 0.9f);
            await Task.Delay(500);  // Petit délai pour la transition
            
            // Masquage de l'écran de chargement
            UpdateLoadingProgress("Ready!", 1f);
            await Task.Delay(1000);  // Affichage du "Ready!" pendant une seconde
            
            if (loadingScreen != null)
                loadingScreen.Hide();
            
            Debug.Log($"NPCs initialized: {npcObjects.Count}");
            
        } catch (Exception e) {
            Debug.LogError($"Error initializing NPCs: {e.Message}");
            UpdateLoadingProgress($"Error: {e.Message}", 1f);
        }
    }
    
    private void UpdateLoadingProgress(string status, float progress = -1f)
    {
        if (loadingScreen != null)
        {
            if (progress < 0)
            {
                currentInitStep++;
                progress = (float)currentInitStep / totalInitSteps;
            }
            loadingScreen.SetProgress(progress, status);
        }
        
        if (showDebugLogs)
            Debug.Log($"Loading: {status} ({progress:P0})");
    }
    
    private async Task LoadNPCResources()
    {
        // Simulation du chargement des ressources
        for (int i = 0; i < 3; i++)
        {
            UpdateLoadingProgress($"Loading resources ({i + 1}/3)...", 0.3f + i * 0.1f);
            await Task.Delay(100);  // Simulation du temps de chargement
        }
    }
    
    private async Task CreateNPC(string npcId)
    {
        try
        {
            // Récupération des données du PNJ
            var npcData = await GetNPCData(npcId);
            
            // Création de l'objet Unity
            var prefabPath = npcData.data.prefab_path ?? "Prefabs/DefaultNPC";
            var prefab = Resources.Load<GameObject>(prefabPath);
            var npcObject = Instantiate(prefab);
            
            // Configuration du contrôleur
            var controller = npcObject.GetComponent<NPCController>();
            if (controller == null)
                controller = npcObject.AddComponent<NPCController>();
            
            controller.Initialize(npcId, npcData);
            
            // Stockage des références
            npcObjects[npcId] = npcObject;
            npcControllers[npcId] = controller;
            
            if (showDebugLogs)
                Debug.Log($"NPC created: {npcId}");
        }
        catch (Exception e)
        {
            Debug.LogError($"Error creating NPC {npcId}: {e.Message}");
        }
    }
    
    private void Update()
    {
        // Mise à jour périodique
        if (Time.time - lastUpdateTime >= updateInterval)
        {
            lastUpdateTime = Time.time;
            UpdateNPCs();
        }
    }
    
    private async void UpdateNPCs()
    {
        try
        {
            // Préparation des données
            var updateData = new Dictionary<string, object>
            {
                ["npc_positions"] = GetNPCPositions(),
                ["npc_animations"] = GetNPCAnimations(),
                ["delta_time"] = Time.deltaTime
            };
            
            // Envoi de la mise à jour
            var response = await SendUpdate(updateData);
            
            // Application des mises à jour
            foreach (var update in response.npc_updates)
            {
                if (npcControllers.TryGetValue(update.Key, out var controller))
                {
                    controller.ApplyUpdate(update.Value);
                }
            }
        }
        catch (Exception e)
        {
            if (showDebugLogs)
                Debug.LogError($"Error updating NPCs: {e.Message}");
        }
    }
    
    private Dictionary<string, Vector3> GetNPCPositions()
    {
        var positions = new Dictionary<string, Vector3>();
        foreach (var kvp in npcObjects)
        {
            positions[kvp.Key] = kvp.Value.transform.position;
        }
        return positions;
    }
    
    private Dictionary<string, string> GetNPCAnimations()
    {
        var animations = new Dictionary<string, string>();
        foreach (var kvp in npcControllers)
        {
            animations[kvp.Key] = kvp.Value.CurrentAnimation;
        }
        return animations;
    }
    
    public async Task<bool> InteractWithNPC(string npcId, string action, Dictionary<string, object> data)
    {
        try
        {
            var request = new
            {
                npc_id = npcId,
                action = action,
                data = data
            };
            
            var response = await SendRequest<APIResponse<object>>("interact", request);
            return response.success;
        }
        catch (Exception e)
        {
            Debug.LogError($"Error interacting with NPC {npcId}: {e.Message}");
            return false;
        }
    }
    
    private async Task<T> SendRequest<T>(string endpoint, object data)
    {
        var url = $"{apiUrl}/{endpoint}";
        var json = JsonConvert.SerializeObject(data);
        
        using (var request = new UnityWebRequest(url, "POST"))
        {
            var bodyRaw = Encoding.UTF8.GetBytes(json);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            
            await request.SendWebRequest();
            
            if (request.result != UnityWebRequest.Result.Success)
            {
                throw new Exception(request.error);
            }
            
            return JsonConvert.DeserializeObject<T>(request.downloadHandler.text);
        }
    }
    
    private async Task<dynamic> GetWorldState()
    {
        return await SendRequest<dynamic>("world", null);
    }
    
    private async Task<dynamic> GetNPCData(string npcId)
    {
        return await SendRequest<dynamic>($"npc/{npcId}", null);
    }
    
    private async Task<dynamic> SendUpdate(Dictionary<string, object> data)
    {
        return await SendRequest<dynamic>("unity/update", data);
    }
    
    private void OnDestroy()
    {
        // Nettoyage
        npcObjects.Clear();
        npcControllers.Clear();
    }
}

// Contrôleur de PNJ pour Unity
public class NPCController : MonoBehaviour
{
    private string npcId;
    private dynamic npcData;
    private string currentAnimation;
    private NavMeshAgent agent;
    private Animator animator;
    
    public string CurrentAnimation => currentAnimation;
    
    public void Initialize(string id, dynamic data)
    {
        npcId = id;
        npcData = data;
        
        // Configuration des composants
        agent = GetComponent<NavMeshAgent>();
        animator = GetComponent<Animator>();
        
        if (agent == null)
            agent = gameObject.AddComponent<NavMeshAgent>();
        
        if (animator == null)
            animator = gameObject.AddComponent<Animator>();
        
        // Configuration initiale
        ApplyInitialState();
    }
    
    private void ApplyInitialState()
    {
        // Position
        if (npcData.data.position != null)
        {
            var pos = npcData.data.position;
            transform.position = new Vector3(pos.x, pos.y, pos.z);
        }
        
        // Animation
        if (npcData.data.animation_state != null)
        {
            currentAnimation = npcData.data.animation_state;
            animator.Play(currentAnimation);
        }
    }
    
    public void ApplyUpdate(NPCUpdate update)
    {
        // Mise à jour de la position cible
        if (update.target_position != null && agent != null)
        {
            agent.SetDestination(update.target_position);
        }
        
        // Mise à jour de l'animation
        if (update.desired_animation != null && 
            update.desired_animation != currentAnimation)
        {
            currentAnimation = update.desired_animation;
            animator.Play(currentAnimation);
        }
        
        // Mise à jour du dialogue
        if (update.dialogue_state != null)
        {
            // Mise à jour de l'UI de dialogue si nécessaire
        }
    }
}
