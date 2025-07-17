using System.Net.Http.Json;
using Microsoft.AspNetCore.Components.Forms;
using ResumeAnalyzer.Shared.Models;

namespace ResumeAnalyzer.Client.Services;

public interface IResumeAnalysisService
{
    Task<AnalysisResponse> AnalyzeResumeAsync(IBrowserFile resume, IBrowserFile jobDescription, int? userId = null);
    Task<AnalysisResponse> AnalyzeResumeWithTextAsync(IBrowserFile resume, string jobDescriptionText, int? userId = null);
    Task<List<AnalysisHistory>> GetAnalysisHistoryAsync(int? userId = null);
    AnalysisResponse? LatestResult { get; }
}

public class ResumeAnalysisService : IResumeAnalysisService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<ResumeAnalysisService> _logger;
    private readonly List<AnalysisHistory> _temporaryHistory = new();

    public ResumeAnalysisService(HttpClient httpClient, ILogger<ResumeAnalysisService> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
    }

    public AnalysisResponse? LatestResult { get; private set; }

    public async Task<AnalysisResponse> AnalyzeResumeAsync(IBrowserFile resume, IBrowserFile jobDescription, int? userId = null)
    {
        try
        {
            using var content = new MultipartFormDataContent();
            
            // Add resume file
            var resumeContent = new StreamContent(resume.OpenReadStream(maxAllowedSize: 10485760)); // 10MB max
            var resumeContentType = GetContentType(resume.Name);
            resumeContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue(resumeContentType);
            content.Add(resumeContent, "resume", resume.Name);
            
            // Add job description file
            var jobContent = new StreamContent(jobDescription.OpenReadStream(maxAllowedSize: 10485760));
            var jobContentType = GetContentType(jobDescription.Name);
            jobContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue(jobContentType);
            content.Add(jobContent, "jobDescription", jobDescription.Name);

            // Add user ID if provided
            if (userId.HasValue)
            {
                content.Add(new StringContent(userId.Value.ToString()), "userId");
            }

            var response = await _httpClient.PostAsync("api/ResumeAnalysis/analyze", content);
            
            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                _logger.LogError("API Error: {StatusCode} - {Error}", response.StatusCode, errorContent);
                throw new HttpRequestException($"API Error: {response.StatusCode} - {errorContent}");
            }

            var analysisResponse = await response.Content.ReadFromJsonAsync<AnalysisResponse>() 
                ?? throw new InvalidOperationException("Failed to deserialize response");
            LatestResult = analysisResponse;

            // For anonymous users, store in temporary history
            if (!userId.HasValue)
            {
                var tempHistory = new AnalysisHistory
                {
                    Id = _temporaryHistory.Count + 1,
                    ResumeName = resume.Name,
                    JobTitle = jobDescription.Name,
                    MatchPercentage = analysisResponse.MatchPercentage,
                    MissingSkills = analysisResponse.MissingSkills,
                    Recommendation = analysisResponse.Recommendation,
                    CreatedAt = DateTime.Now,
                    UserId = null
                };
                _temporaryHistory.Insert(0, tempHistory); // Add to beginning for latest first
            }

            return analysisResponse;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error analyzing resume");
            throw;
        }
    }

    public async Task<AnalysisResponse> AnalyzeResumeWithTextAsync(IBrowserFile resume, string jobDescriptionText, int? userId = null)
    {
        try
        {
            using var content = new MultipartFormDataContent();
            
            // Add resume file
            var resumeContent = new StreamContent(resume.OpenReadStream(maxAllowedSize: 10485760)); // 10MB max
            var resumeContentType = GetContentType(resume.Name);
            resumeContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue(resumeContentType);
            content.Add(resumeContent, "resume", resume.Name);
            
            // Add job description as text file
            var jobTextBytes = System.Text.Encoding.UTF8.GetBytes(jobDescriptionText);
            var jobTextContent = new ByteArrayContent(jobTextBytes);
            jobTextContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("text/plain");
            content.Add(jobTextContent, "jobDescription", "job_description.txt");

            // Add user ID if provided
            if (userId.HasValue)
            {
                content.Add(new StringContent(userId.Value.ToString()), "userId");
            }

            var response = await _httpClient.PostAsync("api/ResumeAnalysis/analyze", content);
            
            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                _logger.LogError("API Error: {StatusCode} - {Error}", response.StatusCode, errorContent);
                throw new HttpRequestException($"API Error: {response.StatusCode} - {errorContent}");
            }

            var analysisResponse = await response.Content.ReadFromJsonAsync<AnalysisResponse>() 
                ?? throw new InvalidOperationException("Failed to deserialize response");
            LatestResult = analysisResponse;

            // For anonymous users, store in temporary history
            if (!userId.HasValue)
            {
                var tempHistory = new AnalysisHistory
                {
                    Id = _temporaryHistory.Count + 1,
                    ResumeName = resume.Name,
                    JobTitle = "Job Description (Text)",
                    MatchPercentage = analysisResponse.MatchPercentage,
                    MissingSkills = analysisResponse.MissingSkills,
                    Recommendation = analysisResponse.Recommendation,
                    CreatedAt = DateTime.Now,
                    UserId = null
                };
                _temporaryHistory.Insert(0, tempHistory); // Add to beginning for latest first
            }

            return analysisResponse;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error analyzing resume with text");
            throw;
        }
    }

    private string GetContentType(string fileName)
    {
        var extension = Path.GetExtension(fileName).ToLowerInvariant();
        return extension switch
        {
            ".pdf" => "application/pdf",
            ".docx" => "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".txt" => "text/plain",
            _ => "application/octet-stream"
        };
    }

    public async Task<List<AnalysisHistory>> GetAnalysisHistoryAsync(int? userId = null)
    {
        try
        {
            if (!userId.HasValue)
            {
                // Return temporary history for anonymous users
                return _temporaryHistory.ToList();
            }

            // For logged-in users, fetch from database
            return await _httpClient.GetFromJsonAsync<List<AnalysisHistory>>($"api/ResumeAnalysis/history?userId={userId.Value}")
                ?? new List<AnalysisHistory>();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error fetching analysis history");
            throw;
        }
    }
} 