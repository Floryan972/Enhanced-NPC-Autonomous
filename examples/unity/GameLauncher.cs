using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections;
using System.Threading.Tasks;
using DG.Tweening;
using UnityEngine.SceneManagement;

public class GameLauncher : MonoBehaviour
{
    [Header("UI References")]
    [SerializeField] private CanvasGroup mainCanvas;
    [SerializeField] private RectTransform logoContainer;
    [SerializeField] private Image logoImage;
    [SerializeField] private TextMeshProUGUI titleText;
    [SerializeField] private Image progressBar;
    [SerializeField] private TextMeshProUGUI progressText;
    [SerializeField] private TextMeshProUGUI statusText;
    [SerializeField] private Button playButton;
    [SerializeField] private Button settingsButton;
    [SerializeField] private Button quitButton;
    
    [Header("Animation Settings")]
    [SerializeField] private float initialDelay = 1f;
    [SerializeField] private float logoAnimationDuration = 2f;
    [SerializeField] private float buttonAnimationDelay = 0.2f;
    [SerializeField] private float loadingBarSpeed = 1f;
    
    [Header("Style Settings")]
    [SerializeField] private Color primaryColor = new Color(0.2f, 0.6f, 1f);
    [SerializeField] private Color secondaryColor = new Color(0.1f, 0.1f, 0.1f, 0.5f);
    
    private bool isInitialized = false;
    private NPCManager npcManager;
    
    private void Start()
    {
        // Configuration initiale
        InitializeUI();
        
        // Démarrage des animations
        StartCoroutine(LauncherSequence());
    }
    
    private void InitializeUI()
    {
        // Configuration des couleurs
        progressBar.color = primaryColor;
        progressBar.transform.parent.GetComponent<Image>().color = secondaryColor;
        
        // Configuration du texte
        titleText.text = "ENA Enhanced NPC Autonomous";
        titleText.color = Color.white;
        
        // Configuration des boutons
        SetupButton(playButton, "PLAY", StartGame);
        SetupButton(settingsButton, "SETTINGS", OpenSettings);
        SetupButton(quitButton, "QUIT", QuitGame);
        
        // Masquage initial
        mainCanvas.alpha = 0f;
        progressBar.fillAmount = 0f;
        SetButtonsVisible(false);
    }
    
    private void SetupButton(Button button, string text, UnityEngine.Events.UnityAction action)
    {
        var buttonText = button.GetComponentInChildren<TextMeshProUGUI>();
        if (buttonText != null)
            buttonText.text = text;
        
        button.onClick.AddListener(action);
        
        // Style du bouton
        var buttonImage = button.GetComponent<Image>();
        if (buttonImage != null)
        {
            buttonImage.color = secondaryColor;
            
            // Animation au survol
            button.onPointerEnter.AddListener(() => {
                buttonImage.DOColor(primaryColor, 0.2f);
            });
            button.onPointerExit.AddListener(() => {
                buttonImage.DOColor(secondaryColor, 0.2f);
            });
        }
    }
    
    private IEnumerator LauncherSequence()
    {
        // Attente initiale
        yield return new WaitForSeconds(initialDelay);
        
        // Fade in du canvas
        mainCanvas.DOFade(1f, 1f);
        
        // Animation du logo
        Vector2 originalPosition = logoContainer.anchoredPosition;
        logoContainer.anchoredPosition = originalPosition + Vector2.up * 100;
        
        yield return new WaitForSeconds(0.5f);
        
        // Animation de descente du logo
        logoContainer.DOAnchorPos(originalPosition, logoAnimationDuration)
            .SetEase(Ease.OutBack);
        
        // Chargement des systèmes en arrière-plan
        InitializeGameSystems();
        
        // Animation de la barre de progression
        while (!isInitialized)
        {
            progressBar.fillAmount = Mathf.MoveTowards(
                progressBar.fillAmount, 0.9f, Time.deltaTime * loadingBarSpeed
            );
            progressText.text = $"{(progressBar.fillAmount * 100):F0}%";
            yield return null;
        }
        
        // Finalisation
        progressBar.DOFillAmount(1f, 0.5f);
        progressText.text = "100%";
        
        yield return new WaitForSeconds(0.5f);
        
        // Affichage des boutons
        ShowButtons();
    }
    
    private async void InitializeGameSystems()
    {
        try
        {
            // Création du gestionnaire NPC
            npcManager = new GameObject("NPCManager").AddComponent<NPCManager>();
            
            // Initialisation
            statusText.text = "Initializing AI System...";
            await Task.Delay(1000);
            
            statusText.text = "Loading NPC Templates...";
            await Task.Delay(1000);
            
            statusText.text = "Preparing Game World...";
            await Task.Delay(1000);
            
            // Initialisation terminée
            isInitialized = true;
            statusText.text = "Ready to Play!";
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Error during initialization: {e.Message}");
            statusText.text = "Error: Failed to initialize game systems";
        }
    }
    
    private void ShowButtons()
    {
        StartCoroutine(AnimateButtons());
    }
    
    private IEnumerator AnimateButtons()
    {
        Button[] buttons = { playButton, settingsButton, quitButton };
        
        foreach (var button in buttons)
        {
            // Position initiale
            var rect = button.GetComponent<RectTransform>();
            var originalPos = rect.anchoredPosition;
            rect.anchoredPosition = originalPos + Vector2.right * 100;
            
            // Affichage et animation
            button.gameObject.SetActive(true);
            rect.DOAnchorPos(originalPos, 0.5f).SetEase(Ease.OutBack);
            
            yield return new WaitForSeconds(buttonAnimationDelay);
        }
    }
    
    private void SetButtonsVisible(bool visible)
    {
        playButton.gameObject.SetActive(visible);
        settingsButton.gameObject.SetActive(visible);
        quitButton.gameObject.SetActive(visible);
    }
    
    // Actions des boutons
    private void StartGame()
    {
        // Animation de sortie
        mainCanvas.DOFade(0f, 1f).OnComplete(() => {
            // Chargement de la scène de jeu
            SceneManager.LoadScene("GameScene");
        });
    }
    
    private void OpenSettings()
    {
        // TODO: Ouvrir le menu des paramètres
        Debug.Log("Settings menu not implemented yet");
    }
    
    private void QuitGame()
    {
        // Animation de sortie
        mainCanvas.DOFade(0f, 1f).OnComplete(() => {
            #if UNITY_EDITOR
                UnityEditor.EditorApplication.isPlaying = false;
            #else
                Application.Quit();
            #endif
        });
    }
    
    private void OnDestroy()
    {
        // Nettoyage des tweens
        DOTween.Kill(logoContainer);
        DOTween.Kill(mainCanvas);
        DOTween.Kill(progressBar);
    }
}
