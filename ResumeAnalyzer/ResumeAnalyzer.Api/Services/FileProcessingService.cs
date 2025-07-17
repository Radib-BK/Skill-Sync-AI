using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;
using iText.Kernel.Pdf;
using iText.Kernel.Pdf.Canvas.Parser;
using iText.Kernel.Pdf.Canvas.Parser.Listener;
using System.Text;

namespace ResumeAnalyzer.Api.Services;

public interface IFileProcessingService
{
    Task<string> ExtractTextFromFileAsync(Stream fileStream, string fileName);
}

public class FileProcessingService : IFileProcessingService
{
    public async Task<string> ExtractTextFromFileAsync(Stream fileStream, string fileName)
    {
        // Create a memory stream copy to ensure we can read it multiple times
        using var memoryStream = new MemoryStream();
        await fileStream.CopyToAsync(memoryStream);
        memoryStream.Position = 0;  // Reset position to start
        
        string extension = Path.GetExtension(fileName).ToLower();
        
        return extension switch
        {
            ".pdf" => await ExtractTextFromPdfAsync(memoryStream),
            ".docx" => await ExtractTextFromDocxAsync(memoryStream),
            ".txt" => await ExtractTextFromTxtAsync(memoryStream),
            _ => throw new ArgumentException("Unsupported file type. Only PDF, DOCX, and TXT files are supported.")
        };
    }

    private async Task<string> ExtractTextFromPdfAsync(Stream fileStream)
    {
        return await Task.Run(() =>
        {
            using var pdfReader = new PdfReader(fileStream);
            using var pdfDocument = new PdfDocument(pdfReader);
            var text = new StringBuilder();

            for (int i = 1; i <= pdfDocument.GetNumberOfPages(); i++)
            {
                var page = pdfDocument.GetPage(i);
                var strategy = new LocationTextExtractionStrategy();
                text.AppendLine(PdfTextExtractor.GetTextFromPage(page, strategy));
            }

            return text.ToString();
        });
    }

    private async Task<string> ExtractTextFromDocxAsync(Stream fileStream)
    {
        return await Task.Run(() =>
        {
            using var wordDocument = WordprocessingDocument.Open(fileStream, false);
            var mainPart = wordDocument.MainDocumentPart;
            if (mainPart?.Document.Body == null)
                throw new InvalidOperationException("The DOCX file is empty or corrupted.");

            var text = new StringBuilder();
            foreach (var paragraph in mainPart.Document.Body.Elements<Paragraph>())
            {
                text.AppendLine(paragraph.InnerText);
            }

            return text.ToString();
        });
    }

    private async Task<string> ExtractTextFromTxtAsync(Stream fileStream)
    {
        return await Task.Run(async () =>
        {
            using var reader = new StreamReader(fileStream);
            return await reader.ReadToEndAsync();
        });
    }
} 