require 'fileutils'

# Check for Launchy, fallback if missing (to allow running without bundle install in some envs)
try_launchy = true
begin
  require 'launchy'
rescue LoadError
  try_launchy = false
  puts "Warning: 'launchy' gem not found. Browser launch might fail or use fallback."
end

# --- Configuration ---
PID_FILE = '/tmp/acto_pids.log'
# Paths are relative to where this script is run (Acto-Sphere/rb/)
BASE_DIR = File.dirname(File.expand_path(__FILE__))
PROJECT_ROOT = File.join(BASE_DIR, '..')

CPP_WATCHER_CMD = File.join(PROJECT_ROOT, 'cpp/monitor')
# Run python analyzer every 5 seconds to keep stats fresh
PYTHON_ANALYZER_CMD = "sh -c 'while true; do python3 #{File.join(PROJECT_ROOT, 'py/analytics.py')} > /dev/null; sleep 5; done'"
NODE_SERVER_CMD = "node #{File.join(PROJECT_ROOT, 'js/server.js')}"
GO_TUI_DIR = File.join(PROJECT_ROOT, 'go')
UPLOAD_SCRIPT_PATH = File.join(PROJECT_ROOT, 'sh/upload.sh')
BROWSER_URL = 'http://localhost:3000/dashboard.html'

# --- PID Management ---

def write_pid(pid)
  File.open(PID_FILE, 'a') { |f| f.puts(pid) }
end

def read_pids
  return [] unless File.exist?(PID_FILE)
  File.readlines(PID_FILE).map(&:chomp).map(&:to_i).select { |pid| pid > 0 }
end

def cleanup_pids
  pids = read_pids
  if pids.empty?
    return
  end

  puts "\nStopping background services..."
  pids.each do |pid|
    begin
      Process.kill('TERM', pid)
    rescue Errno::ESRCH
      # Process already dead
    rescue => e
      STDERR.puts "Error killing process #{pid}: #{e.message}"
    end
  end
  FileUtils.rm_f(PID_FILE)
  puts "Services stopped."
end

# --- Actions ---

def start_ecosystem
  puts "Starting Acto Ecosystem..."
  
  # 1. C++ Monitor
  if File.exist?(CPP_WATCHER_CMD)
    pid = Process.spawn(CPP_WATCHER_CMD, [:out, :err] => '/dev/null')
    write_pid(pid)
    puts " [OK] C++ Monitor started (PID: #{pid})"
  else
    puts " [ERR] C++ Monitor binary not found at #{CPP_WATCHER_CMD}"
  end

  # 2. Python Analyzer (Loop)
  pid_py = Process.spawn(PYTHON_ANALYZER_CMD, [:out, :err] => '/dev/null')
  write_pid(pid_py)
  puts " [OK] Python Analyzer Loop started (PID: #{pid_py})"

  # 3. Node Server
  # We want to see Node output if possible, but for background we usually silence it
  # or log it. Let's silence for the menu cleanlyness.
  pid_node = Process.spawn(NODE_SERVER_CMD, [:out, :err] => '/dev/null')
  write_pid(pid_node)
  puts " [OK] Node.js Server started (PID: #{pid_node})"
  puts "      Dashboard available at #{BROWSER_URL}"
end

def open_tui
  puts "Launching Go TUI..."
  # We use system here because we want it to take over the terminal
  # Assume 'go' is installed
  Dir.chdir(GO_TUI_DIR) do
    system("go run main.go")
  end
end

def open_web_dashboard
  puts "Opening Web Dashboard..."
  begin
    if defined?(Launchy)
      Launchy.open(BROWSER_URL)
    else
      # Fallback for Linux
      system("xdg-open #{BROWSER_URL}")
    end
  rescue => e
    puts "Could not open browser: #{e.message}"
    puts "Please manually visit: #{BROWSER_URL}"
  end
end

def sync_cloud
  puts "Running Cloud Sync..."
  system("bash #{UPLOAD_SCRIPT_PATH}")
end

# --- Main ---

# Register cleanup on exit
at_exit { cleanup_pids }

loop do
  puts "\n========== Acto-Sphere Launcher =========="
  puts "1. Start Acto Ecosystem (Background Services)"
  puts "2. Open TUI (Go Log Monitor)"
  puts "3. Open Web Dashboard"
  puts "4. Sync Cloud"
  puts "5. Exit (Stops all services)"
  print "Select option: "
  
  choice = gets.chomp

  case choice
  when '1'
    start_ecosystem
  when '2'
    open_tui
  when '3'
    open_web_dashboard
  when '4'
    sync_cloud
  when '5', 'exit'
    puts "Exiting..."
    break
  else
    puts "Invalid option."
  end
end
