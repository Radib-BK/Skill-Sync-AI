using System.Text.Json.Serialization;
using System.ComponentModel.DataAnnotations;

namespace ResumeAnalyzer.Shared.Models;

public class AnalysisRequest
{
    [JsonPropertyName("resume_text")]
    public string ResumeText { get; set; } = string.Empty;
    
    [JsonPropertyName("job_text")]
    public string JobText { get; set; } = string.Empty;
}

public class AnalysisResponse
{
    [JsonPropertyName("match_percentage")]
    public float MatchPercentage { get; set; }
    
    [JsonPropertyName("missing_skills")]
    public List<string> MissingSkills { get; set; } = new();
    
    [JsonPropertyName("recommendation")]
    public string Recommendation { get; set; } = string.Empty;
}

public class AnalysisHistory
{
    public int Id { get; set; }
    public string ResumeName { get; set; } = string.Empty;
    public string JobTitle { get; set; } = string.Empty;
    public float MatchPercentage { get; set; }
    public List<string> MissingSkills { get; set; } = new();
    public string Recommendation { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public int? UserId { get; set; }
    public User? User { get; set; }
}

// Authentication Models
public class User
{
    public int Id { get; set; }
    public string Username { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string PasswordHash { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public List<AnalysisHistory> AnalysisHistories { get; set; } = new();
}

public class RegisterRequest
{
    [Required]
    [MinLength(3)]
    public string Username { get; set; } = string.Empty;
    
    [Required]
    [EmailAddress]
    public string Email { get; set; } = string.Empty;
    
    [Required]
    [MinLength(6)]
    public string Password { get; set; } = string.Empty;
    
    [Required]
    [Compare("Password")]
    public string ConfirmPassword { get; set; } = string.Empty;
}

public class LoginRequest
{
    [Required]
    public string Username { get; set; } = string.Empty;
    
    [Required]
    public string Password { get; set; } = string.Empty;
}

public class AuthResponse
{
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public User? User { get; set; }
    public string Token { get; set; } = string.Empty;
}

public class UserSession
{
    public int UserId { get; set; }
    public string Username { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public bool IsAuthenticated { get; set; }
} 