using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections;
using DG.Tweening;

public class LoadingScreen : MonoBehaviour
{
    [Header("References")]
    [SerializeField] private RectTransform logoContainer;
    [SerializeField] private Image logoImage;
    [SerializeField] private Image progressBar;
    [SerializeField] private TextMeshProUGUI progressText;
    [SerializeField] private TextMeshProUGUI statusText;
    [SerializeField] private CanvasGroup mainCanvasGroup;
    
    [Header("Animation Settings")]
    [SerializeField] private float logoBounceDuration = 1f;
    [SerializeField] private float logoFloatAmplitude = 10f;
    [SerializeField] private float logoFloatDuration = 2f;
    [SerializeField] private Color progressBarColor = new Color(0.2f, 0.6f, 1f);
    [SerializeField] private Color progressBarBackgroundColor = new Color(0.1f, 0.1f, 0.1f, 0.5f);
    
    [Header("Text Settings")]
    [SerializeField] private string titleText = "ENA Enhanced NPC Autonomous";
    [SerializeField] private Color titleColor = Color.white;
    [SerializeField] private TMP_FontAsset titleFont;
    
    private void Start()
    {
        InitializeUI();
        StartCoroutine(AnimateLogoEntrance());
    }
    
    private void InitializeUI()
    {
        // Configuration du logo
        logoContainer.anchorMin = new Vector2(1, 0);
        logoContainer.anchorMax = new Vector2(1, 0);
        logoContainer.pivot = new Vector2(1, 0);
        logoContainer.anchoredPosition = new Vector2(-20, 20);
        
        // Configuration de la barre de progression
        progressBar.color = progressBarColor;
        progressBar.transform.parent.GetComponent<Image>().color = progressBarBackgroundColor;
        
        // Configuration du texte
        TextMeshProUGUI titleTMP = logoContainer.GetComponentInChildren<TextMeshProUGUI>();
        if (titleTMP != null)
        {
            titleTMP.text = titleText;
            titleTMP.color = titleColor;
            if (titleFont != null)
                titleTMP.font = titleFont;
        }
        
        // Initialisation des valeurs
        SetProgress(0f, "Initializing...");
        mainCanvasGroup.alpha = 0f;
    }
    
    private IEnumerator AnimateLogoEntrance()
    {
        // Fade in
        mainCanvasGroup.DOFade(1f, 0.5f);
        
        // Animation d'entrée du logo
        Vector2 originalPosition = logoContainer.anchoredPosition;
        logoContainer.anchoredPosition = originalPosition - new Vector2(0, 100);
        
        yield return new WaitForSeconds(0.2f);
        
        // Rebond
        logoContainer.DOAnchorPos(originalPosition, logoBounceDuration)
            .SetEase(Ease.OutBounce);
        
        // Animation de flottement continue
        DOTween.Sequence()
            .Append(logoContainer.DOAnchorPosY(originalPosition.y + logoFloatAmplitude, logoFloatDuration)
                .SetEase(Ease.InOutSine))
            .Append(logoContainer.DOAnchorPosY(originalPosition.y, logoFloatDuration)
                .SetEase(Ease.InOutSine))
            .SetLoops(-1);
    }
    
    public void SetProgress(float progress, string status = "")
    {
        // Mise à jour de la barre de progression
        progressBar.fillAmount = Mathf.Clamp01(progress);
        
        // Mise à jour du texte de progression
        progressText.text = $"{(progress * 100):F0}%";
        
        // Mise à jour du statut
        if (!string.IsNullOrEmpty(status))
            statusText.text = status;
    }
    
    public void Hide()
    {
        // Animation de sortie
        mainCanvasGroup.DOFade(0f, 0.5f).OnComplete(() => {
            gameObject.SetActive(false);
        });
    }
}

[System.Serializable]
public class LoadingScreenConfig
{
    public string Title = "ENA Enhanced NPC Autonomous";
    public Color TitleColor = Color.white;
    public Color ProgressBarColor = new Color(0.2f, 0.6f, 1f);
    public Color ProgressBarBackgroundColor = new Color(0.1f, 0.1f, 0.1f, 0.5f);
    public float LogoBounceDuration = 1f;
    public float LogoFloatAmplitude = 10f;
    public float LogoFloatDuration = 2f;
}
