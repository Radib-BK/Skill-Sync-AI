using System.Text;
using System.Text.Json;
using ResumeAnalyzer.Shared.Models;

namespace ResumeAnalyzer.Api.Services;

public interface IAIServiceClient
{
    Task<AnalysisResponse> AnalyzeResumeAsync(AnalysisRequest request);
}

public class AIServiceClient : IAIServiceClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<AIServiceClient> _logger;

    public AIServiceClient(HttpClient httpClient, ILogger<AIServiceClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
        
        // Configure base address for the AI service
        _httpClient.BaseAddress = new Uri("http://localhost:5002/");
    }

    public async Task<AnalysisResponse> AnalyzeResumeAsync(AnalysisRequest request)
    {
        try
        {
            var content = new StringContent(
                JsonSerializer.Serialize(request),
                Encoding.UTF8,
                "application/json");

            var response = await _httpClient.PostAsync("analyze", content);
            
            // Read the response content even if it's an error
            var responseContent = await response.Content.ReadAsStringAsync();
            
            if (!response.IsSuccessStatusCode)
            {
                _logger.LogError("AI service returned error: Status {StatusCode}, Content: {Content}", 
                    response.StatusCode, responseContent);
                throw new ApplicationException($"AI service error: {response.StatusCode} - {responseContent}");
            }

            var result = JsonSerializer.Deserialize<AnalysisResponse>(responseContent);

            if (result == null)
                throw new InvalidOperationException("Failed to deserialize AI service response");

            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error calling AI service");
            throw new ApplicationException("Failed to analyze resume. Please try again later.", ex);
        }
    }
} 