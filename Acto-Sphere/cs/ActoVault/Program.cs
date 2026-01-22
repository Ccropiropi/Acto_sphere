using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using System.Linq;

namespace ActoVault
{
    class Program
    {
        // Configuration
        private static readonly string VaultDir = Path.Combine("..", "..", "..", "vault_storage");
        
        static void Main(string[] args)
        {
            if (args.Length == 0)
            {
                Console.WriteLine("Usage: ActoVault <file_path> | --test");
                return;
            }

            if (args[0] == "--test")
            {
                RunTests();
                return;
            }

            string sourcePath = args[0];
            try
            {
                ProcessFile(sourcePath);
            }
            catch (Exception ex)
            {
                LogError($"Critical Failure: {ex.Message}");
            }
        }

        static void ProcessFile(string sourcePath)
        {
            // 1. Validation
            if (!File.Exists(sourcePath))
            {
                LogError($"File not found: {sourcePath}");
                return;
            }

            // 2. Setup Vault Directory
            // Correcting relative path based on execution from bin/Debug/net6.0 usually, 
            // but assuming run from project root for simplicity in path logic:
            // Let's resolve absolute path to be safe.
            string absVaultDir = Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, VaultDir));
            
            if (!Directory.Exists(absVaultDir))
            {
                Directory.CreateDirectory(absVaultDir);
                Log("Created vault directory at: " + absVaultDir);
            }

            // 3. Encrypt
            string fileName = Path.GetFileName(sourcePath);
            string destPath = Path.Combine(absVaultDir, fileName + ".enc");
            string keyPath = Path.Combine(absVaultDir, fileName + ".key");

            byte[] key = new byte[32]; // 256 bits
            byte[] nonce = new byte[12]; // 96 bits for GCM
            byte[] tag = new byte[16]; // 128 bit tag

            using (var rng = RandomNumberGenerator.Create())
            {
                rng.GetBytes(key);
                rng.GetBytes(nonce);
            }

            Log($"Encrypting {fileName}...");

            byte[] plaintext = File.ReadAllBytes(sourcePath);
            byte[] ciphertext = new byte[plaintext.Length];

            using (var aes = new AesGcm(key))
            {
                aes.Encrypt(nonce, plaintext, ciphertext, tag);
            }

            // 4. Save Encrypted Data (Nonce + Tag + Ciphertext)
            // Structure: [Nonce 12b][Tag 16b][Ciphertext N]
            using (var fs = new FileStream(destPath, FileMode.Create))
            using (var bw = new BinaryWriter(fs))
            {
                bw.Write(nonce);
                bw.Write(tag);
                bw.Write(ciphertext);
            }

            // Save key (In a real scenario, this would be handled securely!)
            File.WriteAllBytes(keyPath, key);

            Log($"Success! Encrypted file saved to: {destPath}");
            Log($"Key saved to: {keyPath} (Keep this safe!)");

            // 5. Move (Delete original)
            File.Delete(sourcePath);
            Log($"Original file deleted: {sourcePath}");
        }

        static void Log(string message)
        {
            Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] [INFO] {message}");
        }

        static void LogError(string message)
        {
            Console.ForegroundColor = ConsoleColor.Red;
            Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] [ERROR] {message}");
            Console.ResetColor();
        }

        // --- Unit Tests ---
        static void RunTests()
        {
            Console.WriteLine("Running Unit Tests...");
            
            try 
            {
                Test_Encryption_Decryption();
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine("All Tests Passed!");
                Console.ResetColor();
            }
            catch (Exception ex)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"Test Failed: {ex.Message}");
                Console.ResetColor();
            }
        }

        static void Test_Encryption_Decryption()
        {
            string testMsg = "Hello Acto-Sphere!";
            byte[] plaintext = Encoding.UTF8.GetBytes(testMsg);
            byte[] key = new byte[32];
            byte[] nonce = new byte[12];
            byte[] tag = new byte[16];
            byte[] ciphertext = new byte[plaintext.Length];

            using (var rng = RandomNumberGenerator.Create())
            {
                rng.GetBytes(key);
                rng.GetBytes(nonce);
            }

            // Encrypt
            using (var aes = new AesGcm(key))
            {
                aes.Encrypt(nonce, plaintext, ciphertext, tag);
            }

            // Decrypt
            byte[] decrypted = new byte[ciphertext.Length];
            using (var aes = new AesGcm(key))
            {
                aes.Decrypt(nonce, ciphertext, tag, decrypted);
            }

            string resultMsg = Encoding.UTF8.GetString(decrypted);

            if (testMsg != resultMsg)
            {
                throw new Exception("Decrypted content does not match original.");
            }
            
            Console.WriteLine(" - Encryption/Decryption Cycle: OK");
        }
    }
}
