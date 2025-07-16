using Microsoft.EntityFrameworkCore;
using ResumeAnalyzer.Shared.Models;
using System.Text.Json;

namespace ResumeAnalyzer.Api.Data;

public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
    }

    public DbSet<AnalysisHistory> AnalysisHistories { get; set; } = null!;
    public DbSet<User> Users { get; set; } = null!;

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Configure User entity
        modelBuilder.Entity<User>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Username).IsRequired().HasMaxLength(50);
            entity.Property(e => e.Email).IsRequired().HasMaxLength(100);
            entity.Property(e => e.PasswordHash).IsRequired();
            entity.Property(e => e.CreatedAt)
                .HasDefaultValueSql("CURRENT_TIMESTAMP(6)")
                .ValueGeneratedOnAdd();
            
            // Add unique constraints
            entity.HasIndex(e => e.Username).IsUnique();
            entity.HasIndex(e => e.Email).IsUnique();
        });

        // Configure AnalysisHistory entity
        modelBuilder.Entity<AnalysisHistory>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.ResumeName).IsRequired();
            entity.Property(e => e.JobTitle).IsRequired();
            entity.Property(e => e.MatchPercentage).IsRequired();
            entity.Property(e => e.Recommendation).IsRequired();
            entity.Property(e => e.UserId).IsRequired(false);
            entity.Property(e => e.CreatedAt)
                .HasDefaultValueSql("CURRENT_TIMESTAMP(6)")
                .ValueGeneratedOnAdd();
            
            // Store MissingSkills as JSON
            entity.Property(e => e.MissingSkills)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, new JsonSerializerOptions()),
                    v => JsonSerializer.Deserialize<List<string>>(v, new JsonSerializerOptions())!)
                .HasColumnType("json");
            
            // Configure relationship with User
            entity.HasOne(e => e.User)
                .WithMany(u => u.AnalysisHistories)
                .HasForeignKey(e => e.UserId)
                .OnDelete(DeleteBehavior.Cascade);
        });
    }
} 