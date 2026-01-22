#include <iostream>
#include <filesystem>
#include <fstream>
#include <map>
#include <thread>
#include <chrono>
#include <bitset>
#include <vector>
#include <ctime>
#include <iomanip>
#include <sstream>

namespace fs = std::filesystem;

// Configuration
const fs::path TARGET_FOLDER = "./target_folder";
const fs::path LOG_FILE = "../dat/json/changes_log.json";
const int POLL_INTERVAL_MS = 1000;

// Helper to get current timestamp string
std::string get_timestamp() {
    auto now = std::chrono::system_clock::now();
    std::time_t now_time = std::chrono::system_clock::to_time_t(now);
    std::stringstream ss;
    ss << std::put_time(std::localtime(&now_time), "%Y-%m-%d %H:%M:%S");
    return ss.str();
}

// Function to log changes to JSON file
void log_change(const std::string& filename, const std::string& change_type) {
    // Open in append mode
    std::ofstream log_stream(LOG_FILE, std::ios::app);
    if (!log_stream.is_open()) {
        std::cerr << "Error: Could not open log file at " << LOG_FILE << std::endl;
        return;
    }

    // Simple JSON object append (JSON Lines format for simplicity in appending)
    log_stream << "{"
               << "\"timestamp\": \"" << get_timestamp() << "\", "
               << "\"file\": \"" << filename << "\", "
               << "\"change\": \"" << change_type << "\""
               << "}" << std::endl;
}

// Function to display first 50 bytes in binary
void print_binary_preview(const fs::path& filepath) {
    std::ifstream file(filepath, std::ios::binary);
    if (!file.is_open()) return;

    std::cout << ">>> Binary Preview (First 50 bytes) for " << filepath.filename() << ":\n";
    
    char buffer[50];
    file.read(buffer, 50);
    std::streamsize bytes_read = file.gcount();

    for (int i = 0; i < bytes_read; ++i) {
        // Convert char to unsigned char for correct bit representation
        std::bitset<8> bits(static_cast<unsigned char>(buffer[i]));
        std::cout << bits << " ";
        if ((i + 1) % 10 == 0) std::cout << "\n"; // Newline every 10 bytes for readability
    }
    std::cout << "\n------------------------------------------------\n";
}

int main() {
    if (!fs::exists(TARGET_FOLDER)) {
        fs::create_directory(TARGET_FOLDER);
        std::cout << "Created directory: " << TARGET_FOLDER << std::endl;
    }

    std::cout << "Monitoring " << TARGET_FOLDER << " for changes..." << std::endl;
    std::cout << "Logging to " << LOG_FILE << std::endl;

    // Store last write time of files
    std::map<std::string, fs::file_time_type> file_records;

    // Initial scan
    for (const auto& entry : fs::directory_iterator(TARGET_FOLDER)) {
        if (entry.is_regular_file()) {
            file_records[entry.path().filename().string()] = entry.last_write_time();
        }
    }

    while (true) {
        std::map<std::string, fs::file_time_type> current_files;
        
        // Scan current directory state
        try {
            for (const auto& entry : fs::directory_iterator(TARGET_FOLDER)) {
                if (entry.is_regular_file()) {
                    current_files[entry.path().filename().string()] = entry.last_write_time();
                }
            }
        } catch (const fs::filesystem_error& e) {
            std::cerr << "Filesystem error: " << e.what() << std::endl;
            std::this_thread::sleep_for(std::chrono::milliseconds(POLL_INTERVAL_MS));
            continue;
        }

        // Check for CREATED and MODIFIED files
        for (const auto& [name, time] : current_files) {
            if (file_records.find(name) == file_records.end()) {
                // New file
                std::cout << "[CREATED] " << name << std::endl;
                log_change(name, "CREATED");
                print_binary_preview(TARGET_FOLDER / name);
            } else {
                // Existing file, check time
                if (file_records[name] != time) {
                    std::cout << "[MODIFIED] " << name << std::endl;
                    log_change(name, "MODIFIED");
                    print_binary_preview(TARGET_FOLDER / name);
                }
            }
        }

        // Check for DELETED files
        for (const auto& [name, time] : file_records) {
            if (current_files.find(name) == current_files.end()) {
                std::cout << "[DELETED] " << name << std::endl;
                log_change(name, "DELETED");
            }
        }

        // Update records
        file_records = current_files;

        std::this_thread::sleep_for(std::chrono::milliseconds(POLL_INTERVAL_MS));
    }

    return 0;
}
