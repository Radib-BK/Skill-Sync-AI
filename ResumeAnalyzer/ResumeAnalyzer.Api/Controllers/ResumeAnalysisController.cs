using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using ResumeAnalyzer.Api.Data;
using ResumeAnalyzer.Api.Services;
using ResumeAnalyzer.Shared.Models;

namespace ResumeAnalyzer.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ResumeAnalysisController : ControllerBase
{
    private readonly IFileProcessingService _fileProcessingService;
    private readonly IAIServiceClient _aiServiceClient;
    private readonly ApplicationDbContext _dbContext;
    private readonly ILogger<ResumeAnalysisController> _logger;

    public ResumeAnalysisController(
        IFileProcessingService fileProcessingService,
        IAIServiceClient aiServiceClient,
        ApplicationDbContext dbContext,
        ILogger<ResumeAnalysisController> logger)
    {
        _fileProcessingService = fileProcessingService;
        _aiServiceClient = aiServiceClient;
        _dbContext = dbContext;
        _logger = logger;
    }

    [HttpPost("analyze")]
    public async Task<ActionResult<AnalysisResponse>> AnalyzeResume(
        [FromForm] IFormFile resume,
        [FromForm] IFormFile jobDescription,
        [FromForm] int? userId = null)
    {
        try
        {
            _logger.LogInformation("Starting resume analysis for files: {ResumeFile}, {JobFile}", 
                resume.FileName, jobDescription.FileName);

            // Validate files are provided
            if (resume == null || jobDescription == null)
            {
                return BadRequest("Both resume and job description files are required.");
            }

            // Validate file sizes (max 10MB)
            if (resume.Length > 10485760 || jobDescription.Length > 10485760)
            {
                return BadRequest("File size exceeds maximum limit of 10MB.");
            }

            // Validate file types
            if (!IsValidFileType(resume.FileName) || !IsValidFileType(jobDescription.FileName))
            {
                return BadRequest("Invalid file type. Only PDF and DOCX files are supported.");
            }

            // Extract text from files
            string resumeText;
            string jobText;
            
            try
            {
                resumeText = await _fileProcessingService.ExtractTextFromFileAsync(resume.OpenReadStream(), resume.FileName);
                jobText = await _fileProcessingService.ExtractTextFromFileAsync(jobDescription.OpenReadStream(), jobDescription.FileName);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error extracting text from files");
                return StatusCode(500, "Error processing files. Please ensure the files are not corrupted.");
            }

            // Validate extracted text
            if (string.IsNullOrWhiteSpace(resumeText) || string.IsNullOrWhiteSpace(jobText))
            {
                return BadRequest("Could not extract text from one or both files. Please ensure the files contain readable text.");
            }

            // Call AI service
            var request = new AnalysisRequest
            {
                ResumeText = resumeText,
                JobText = jobText
            };

            try
            {
                var analysisResult = await _aiServiceClient.AnalyzeResumeAsync(request);

                // Save to database only if user is logged in
                if (userId.HasValue)
                {
                    var history = new AnalysisHistory
                    {
                        ResumeName = resume.FileName,
                        JobTitle = jobDescription.FileName,
                        MatchPercentage = analysisResult.MatchPercentage,
                        MissingSkills = analysisResult.MissingSkills,
                        Recommendation = analysisResult.Recommendation,
                        UserId = userId.Value,
                        CreatedAt = DateTime.UtcNow
                    };

                    _dbContext.AnalysisHistories.Add(history);
                    await _dbContext.SaveChangesAsync();
                }

                return Ok(analysisResult);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error from AI service");
                return StatusCode(500, "Error analyzing resume. The AI service may be unavailable.");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected error during resume analysis");
            return StatusCode(500, "An unexpected error occurred while processing your request.");
        }
    }

    [HttpGet("history")]
    public async Task<ActionResult<List<AnalysisHistory>>> GetHistory([FromQuery] int? userId = null)
    {
        try
        {
            if (!userId.HasValue)
            {
                // Return empty list for anonymous users (they don't have persistent history)
                return Ok(new List<AnalysisHistory>());
            }

            var history = await _dbContext.AnalysisHistories
                .Where(h => h.UserId == userId.Value)
                .OrderByDescending(h => h.CreatedAt)
                .ToListAsync();

            return Ok(history);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving analysis history");
            return StatusCode(500, "An error occurred while retrieving the analysis history.");
        }
    }

    private bool IsValidFileType(string fileName)
    {
        var extension = Path.GetExtension(fileName).ToLower();
        return extension == ".pdf" || extension == ".docx";
    }
} 