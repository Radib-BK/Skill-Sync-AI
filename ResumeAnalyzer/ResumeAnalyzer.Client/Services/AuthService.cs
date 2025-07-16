using ResumeAnalyzer.Shared.Models;
using System.Net.Http.Json;
using System.Text.Json;
using Microsoft.JSInterop;

namespace ResumeAnalyzer.Client.Services;

public interface IAuthService
{
    Task<AuthResponse> LoginAsync(LoginRequest request);
    Task<AuthResponse> RegisterAsync(RegisterRequest request);
    Task LogoutAsync();
    Task<UserSession?> GetCurrentUserAsync();
    Task<bool> IsAuthenticatedAsync();
}

public class AuthService : IAuthService
{
    private readonly HttpClient _httpClient;
    private readonly IJSRuntime _jsRuntime;
    private static UserSession? _currentUser; // Make static to persist across instances
    private const string TokenKey = "auth_token";
    private const string UserKey = "current_user";

    public AuthService(HttpClient httpClient, IJSRuntime jsRuntime)
    {
        _httpClient = httpClient;
        _jsRuntime = jsRuntime;
    }

    public async Task<AuthResponse> LoginAsync(LoginRequest request)
    {
        try
        {
            var response = await _httpClient.PostAsJsonAsync("api/auth/login", request);
            
            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                return new AuthResponse { Success = false, Message = $"Server error: {errorContent}" };
            }
            
            var result = await response.Content.ReadFromJsonAsync<AuthResponse>();

            if (result?.Success == true && result.User != null)
            {
                _currentUser = new UserSession
                {
                    UserId = result.User.Id,
                    Username = result.User.Username,
                    Email = result.User.Email,
                    IsAuthenticated = true
                };

                Console.WriteLine($"Login successful - created user session: {_currentUser.Username}");
                
                // Store token and user info in localStorage
                await StoreAuthDataAsync(result.Token, _currentUser);
                Console.WriteLine($"Login successful - stored user: {_currentUser.Username}");
            }

            return result ?? new AuthResponse { Success = false, Message = "Login failed" };
        }
        catch (Exception ex)
        {
            return new AuthResponse { Success = false, Message = $"Login error: {ex.Message}" };
        }
    }

    public async Task<AuthResponse> RegisterAsync(RegisterRequest request)
    {
        try
        {
            var response = await _httpClient.PostAsJsonAsync("api/auth/register", request);
            
            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                return new AuthResponse { Success = false, Message = $"Server error: {errorContent}" };
            }
            
            var result = await response.Content.ReadFromJsonAsync<AuthResponse>();

            if (result?.Success == true && result.User != null)
            {
                _currentUser = new UserSession
                {
                    UserId = result.User.Id,
                    Username = result.User.Username,
                    Email = result.User.Email,
                    IsAuthenticated = true
                };

                // Store token and user info in localStorage
                await StoreAuthDataAsync(result.Token, _currentUser);
            }

            return result ?? new AuthResponse { Success = false, Message = "Registration failed" };
        }
        catch (Exception ex)
        {
            return new AuthResponse { Success = false, Message = $"Registration error: {ex.Message}" };
        }
    }

    public async Task LogoutAsync()
    {
        try
        {
            await _httpClient.PostAsync("api/auth/logout", null);
        }
        catch
        {
            // Ignore errors on logout
        }
        finally
        {
            _currentUser = null;
            await ClearAuthDataAsync();
        }
    }

    public async Task<UserSession?> GetCurrentUserAsync()
    {
        // If we have a current user in memory, return it
        if (_currentUser != null)
        {
            Console.WriteLine($"Returning current user from memory: {_currentUser.Username}");
            return _currentUser;
        }

        // Only check localStorage if we don't have a user in memory (e.g., after app restart)
        try
        {
            var userJson = await GetFromLocalStorageAsync(UserKey);
            if (!string.IsNullOrEmpty(userJson))
            {
                _currentUser = JsonSerializer.Deserialize<UserSession>(userJson);
                Console.WriteLine($"Loaded user from storage: {_currentUser?.Username}");
                return _currentUser;
            }
            else
            {
                Console.WriteLine("No user data found in storage");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error loading user: {ex.Message}");
        }

        return null;
    }

    public async Task<bool> IsAuthenticatedAsync()
    {
        // First check if we have a user in memory
        if (_currentUser?.IsAuthenticated == true)
        {
            return true;
        }

        // If not in memory, check localStorage
        var user = await GetCurrentUserAsync();
        return user?.IsAuthenticated == true;
    }

    private async Task StoreAuthDataAsync(string token, UserSession user)
    {
        await SetLocalStorageAsync(TokenKey, token);
        var userJson = JsonSerializer.Serialize(user);
        await SetLocalStorageAsync(UserKey, userJson);
        Console.WriteLine($"Stored user data: {userJson}");
    }

    private async Task ClearAuthDataAsync()
    {
        await RemoveFromLocalStorageAsync(TokenKey);
        await RemoveFromLocalStorageAsync(UserKey);
    }

    // Real localStorage using JSInterop
    private async Task<string?> GetFromLocalStorageAsync(string key)
    {
        try
        {
            var value = await _jsRuntime.InvokeAsync<string>("localStorage.getItem", key);
            Console.WriteLine($"Getting from localStorage - Key: {key}, Value: {(value != null ? value.Substring(0, Math.Min(100, value.Length)) : "null")}...");
            return value;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error getting from localStorage: {ex.Message}");
            return null;
        }
    }

    private async Task SetLocalStorageAsync(string key, string value)
    {
        try
        {
            await _jsRuntime.InvokeVoidAsync("localStorage.setItem", key, value);
            Console.WriteLine($"Setting localStorage - Key: {key}, Value: {(value != null ? value.Substring(0, Math.Min(100, value.Length)) : "null")}...");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error setting localStorage: {ex.Message}");
        }
    }

    private async Task RemoveFromLocalStorageAsync(string key)
    {
        try
        {
            await _jsRuntime.InvokeVoidAsync("localStorage.removeItem", key);
            Console.WriteLine($"Removed from localStorage - Key: {key}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error removing from localStorage: {ex.Message}");
        }
    }
} 