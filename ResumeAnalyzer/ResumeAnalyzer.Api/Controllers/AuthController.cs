using Microsoft.AspNetCore.Mvc;
using ResumeAnalyzer.Api.Services;
using ResumeAnalyzer.Shared.Models;

namespace ResumeAnalyzer.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class AuthController : ControllerBase
{
    private readonly IAuthService _authService;

    public AuthController(IAuthService authService)
    {
        _authService = authService;
    }

    [HttpPost("register")]
    public async Task<ActionResult<AuthResponse>> Register([FromBody] RegisterRequest request)
    {
        if (!ModelState.IsValid)
        {
            var errors = ModelState.Values.SelectMany(v => v.Errors).Select(e => e.ErrorMessage);
            return BadRequest(new AuthResponse
            {
                Success = false,
                Message = $"Invalid input data: {string.Join(", ", errors)}"
            });
        }

        var result = await _authService.RegisterAsync(request);
        
        if (result.Success)
        {
            return Ok(result);
        }
        
        return BadRequest(result);
    }

    [HttpPost("login")]
    public async Task<ActionResult<AuthResponse>> Login([FromBody] LoginRequest request)
    {
        if (!ModelState.IsValid)
        {
            var errors = ModelState.Values.SelectMany(v => v.Errors).Select(e => e.ErrorMessage);
            return BadRequest(new AuthResponse
            {
                Success = false,
                Message = $"Invalid input data: {string.Join(", ", errors)}"
            });
        }

        var result = await _authService.LoginAsync(request);
        
        if (result.Success)
        {
            return Ok(result);
        }
        
        return Unauthorized(result);
    }

    [HttpPost("logout")]
    public ActionResult Logout()
    {
        // For now, logout is handled client-side by clearing the token
        // In a real application, you might want to invalidate the token on the server
        return Ok(new { Success = true, Message = "Logout successful" });
    }

    [HttpGet("user/{id}")]
    public async Task<ActionResult<User>> GetUser(int id)
    {
        var user = await _authService.GetUserByIdAsync(id);
        
        if (user == null)
        {
            return NotFound(new { Success = false, Message = "User not found" });
        }
        
        return Ok(user);
    }

    [HttpGet("validate")]
    public ActionResult ValidateToken()
    {
        // Simple token validation endpoint
        // In a real application, you would validate the JWT token here
        return Ok(new { Success = true, Message = "Token is valid" });
    }
} 