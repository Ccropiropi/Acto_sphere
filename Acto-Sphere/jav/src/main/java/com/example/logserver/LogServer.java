package com.example.logserver;

import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.file.Files;
import java.nio.file.Paths;

public class LogServer {
    private static final int PORT = 8080;
    // Path relative to where the command is typically run (Project Root) 
    // or absolute path. Adjusted here to look for the 'dat' folder.
    private static final String LOG_FILE_PATH = "../../../../../../../dat/json/changes_log.json"; 

    public static void main(String[] args) {
        System.out.println("Starting Log Server on port " + PORT + "...");
        
        // Resolve file path safely
        File file = new File(LOG_FILE_PATH);
        try {
            // Fallback for different execution contexts
            if (!file.exists()) {
                file = new File("Acto-Sphere/dat/json/changes_log.json");
            }
            if (!file.exists()) {
                 // Absolute fallback for this specific environment
                 file = new File("/home/zrain/Project/any app/type a/Acto-Sphere/dat/json/changes_log.json");
            }
            
            System.out.println("Serving file: " + file.getAbsolutePath());
        } catch (Exception e) {
             System.err.println("Path resolution error: " + e.getMessage());
        }

        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            while (true) {
                System.out.println("Waiting for client connection...");
                try (Socket clientSocket = serverSocket.accept();
                     PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);
                     BufferedReader fileReader = new BufferedReader(new FileReader(file))) {
                    
                    System.out.println("Client connected: " + clientSocket.getInetAddress());
                    
                    String line;
                    while ((line = fileReader.readLine()) != null) {
                        out.println(line);
                    }
                    
                    System.out.println("Data sent successfully.");
                    
                } catch (FileNotFoundException e) {
                    System.err.println("Error: changes_log.json not found.");
                } catch (IOException e) {
                    System.err.println("Error handling client: " + e.getMessage());
                }
            }
        } catch (IOException e) {
            System.err.println("Server exception: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
