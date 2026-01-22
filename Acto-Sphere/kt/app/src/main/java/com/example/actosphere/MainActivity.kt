package com.example.actosphere

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.Socket

class MainActivity : AppCompatActivity() {

    private lateinit var tvLogDisplay: TextView
    private lateinit var btnSync: Button

    // IMPORTANT: Replace this with your Laptop's actual Local IP (e.g., 192.168.1.X)
    // "10.0.2.2" is special alias for localhost when running on Android Emulator
    private val SERVER_IP = "10.0.2.2" 
    private val SERVER_PORT = 8080

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        tvLogDisplay = findViewById(R.id.tvLogDisplay)
        btnSync = findViewById(R.id.btnSync)

        btnSync.setOnClickListener {
            fetchLogData(SERVER_IP)
        }
    }

    private fun fetchLogData(ipAddress: String) {
        tvLogDisplay.text = "Connecting to $ipAddress:$SERVER_PORT..."
        
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val socket = Socket(ipAddress, SERVER_PORT)
                val reader = BufferedReader(InputStreamReader(socket.getInputStream()))
                val stringBuilder = StringBuilder()
                
                var line: String?
                while (reader.readLine().also { line = it } != null) {
                    stringBuilder.append(line).append("\n")
                }
                
                socket.close()

                withContext(Dispatchers.Main) {
                    if (stringBuilder.isNotEmpty()) {
                        tvLogDisplay.text = stringBuilder.toString()
                    } else {
                        tvLogDisplay.text = "Connected, but log file is empty."
                    }
                }

            } catch (e: Exception) {
                e.printStackTrace()
                withContext(Dispatchers.Main) {
                    tvLogDisplay.text = "Error: ${e.localizedMessage}\n\nMake sure server is running and IP is correct."
                }
            }
        }
    }
}
