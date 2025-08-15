# app.py - Final version without STT (Ready for submission)
import gradio as gr
import requests
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration - matches your backend
API_BASE = "http://127.0.0.1:8000"

# Global variable to store last analysis results for map display
last_analysis_data = {}

def speak_text(text):
    """Convert text to speech using your backend TTS endpoint"""
    if not text or text.strip() == "":
        return None
    
    try:
        # Call your backend TTS endpoint
        payload = {
            "text": text,
            "voice": "nova"  # Options: alloy, echo, fable, onyx, nova, shimmer
        }
        
        response = requests.post(
            f"{API_BASE}/tts", 
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            # Save the audio to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tmp_file.write(response.content)
                return tmp_file.name
        else:
            print(f"TTS Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to TTS service. Make sure backend is running.")
        return None
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

def generate_hospital_map_html(hospitals, user_location=None):
    """Generate HTML for displaying hospital locations"""
    if not hospitals:
        return "<p>No hospital data available. Please run analysis with location data first.</p>"
    
    html = """
    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6;">
        <h4 style="margin-top: 0; color: #2196f3;">🏥 Nearby Hospitals & Emergency Services</h4>
    """
    
    for i, hospital in enumerate(hospitals[:5], 1):
        name = hospital.get('name', 'Unknown Hospital')
        rating = hospital.get('rating', 'N/A')
        address = hospital.get('address', 'Address not available')
        maps_url = hospital.get('maps_url', '#')
        
        # Status indicator
        status_color = "#4caf50" if hospital.get('open_now') else "#ff9800"
        status_text = "Open Now" if hospital.get('open_now') else "Hours Unknown"
        
        html += f"""
        <div style="background: white; margin: 10px 0; padding: 12px; border-radius: 6px; border-left: 4px solid #2196f3;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h5 style="margin: 0; color: #1976d2;">{i}. {name}</h5>
                <span style="background: {status_color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">
                    {status_text}
                </span>
            </div>
            <p style="margin: 5px 0; color: #666;">📍 {address}</p>
        """
        
        if rating != 'N/A':
            stars = "⭐" * int(float(rating)) if isinstance(rating, (int, float)) else "⭐"
            html += f"<p style=\"margin: 5px 0; color: #666;\">⭐ {rating} {stars}</p>"
        
        # Action buttons
        html += f"""
            <div style="margin-top: 8px;">
                <a href="{maps_url}" target="_blank" 
                   style="background: #2196f3; color: white; padding: 6px 12px; text-decoration: none; border-radius: 4px; margin-right: 8px; font-size: 12px;">
                   🗺️ View on Maps
                </a>
        """
        
        # Add directions link if coordinates available
        location = hospital.get('location', {})
        if location.get('lat') and location.get('lng'):
            directions_url = f"https://www.google.com/maps/dir/?api=1&destination={location['lat']},{location['lng']}"
            html += f"""
                <a href="{directions_url}" target="_blank"
                   style="background: #4caf50; color: white; padding: 6px 12px; text-decoration: none; border-radius: 4px; margin-right: 8px; font-size: 12px;">
                   🧭 Directions
                </a>
            """
        
        html += "</div></div>"
    
    # Add general map links
    html += """
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #dee2e6;">
            <h5>🔍 Find More Emergency Services:</h5>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <a href="https://www.google.com/maps/search/hospital+near+me" target="_blank"
                   style="background: #ff5722; color: white; padding: 8px 12px; text-decoration: none; border-radius: 4px; font-size: 12px;">
                   🏥 All Hospitals
                </a>
                <a href="https://www.google.com/maps/search/urgent+care+near+me" target="_blank"
                   style="background: #ff9800; color: white; padding: 8px 12px; text-decoration: none; border-radius: 4px; font-size: 12px;">
                   🚑 Urgent Care
                </a>
                <a href="https://www.google.com/maps/search/emergency+room+near+me" target="_blank"
                   style="background: #f44336; color: white; padding: 8px 12px; text-decoration: none; border-radius: 4px; font-size: 12px;">
                   🆘 Emergency Rooms
                </a>
                <a href="https://www.google.com/maps/search/pharmacy+near+me" target="_blank"
                   style="background: #9c27b0; color: white; padding: 8px 12px; text-decoration: none; border-radius: 4px; font-size: 12px;">
                   💊 Pharmacies
                </a>
            </div>
        </div>
    """
    
    html += "</div>"
    return html

def show_general_hospitals():
    """Show general hospital map"""
    return """
    <div style="text-align: center; padding: 20px;">
        <h3>🏥 Finding All Nearby Hospitals...</h3>
        <p><a href="https://www.google.com/maps/search/hospital+near+me" target="_blank" 
              style="background: #2196f3; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px;">
           🗺️ Open Google Maps - All Hospitals
        </a></p>
        <p style="color: #666; margin-top: 10px;">This will open Google Maps showing all hospitals near your current location.</p>
    </div>
    """

def show_urgent_care():
    """Show urgent care centers"""
    return """
    <div style="text-align: center; padding: 20px;">
        <h3>🚑 Finding Urgent Care Centers...</h3>
        <p><a href="https://www.google.com/maps/search/urgent+care+near+me" target="_blank"
              style="background: #ff9800; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px;">
           🗺️ Open Google Maps - Urgent Care
        </a></p>
        <p style="color: #666; margin-top: 10px;">For non-emergency medical needs that require immediate attention.</p>
    </div>
    """

def show_emergency_rooms():
    """Show emergency rooms"""
    return """
    <div style="text-align: center; padding: 20px;">
        <h3>🆘 Finding Emergency Rooms...</h3>
        <p><a href="https://www.google.com/maps/search/emergency+room+near+me" target="_blank"
              style="background: #f44336; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px;">
           🗺️ Open Google Maps - Emergency Rooms
        </a></p>
        <p style="color: #666; margin-top: 10px;">For life-threatening emergencies requiring immediate medical attention.</p>
    </div>
    """

def analyze_symptoms(symptoms, age, gender, lat, lon, city, country):
    """Analyze symptoms using your backend /assist endpoint"""
    global last_analysis_data
    
    if not symptoms or symptoms.strip() == "":
        return "⚠️ Please describe your symptoms first.", "<p>No analysis data available</p>"
    
    # Prepare payload according to your models.py structure
    payload = {
        "symptoms": symptoms,
        "user": {
            "age": int(age) if age else None,
            "gender": gender if gender else None,
            "latitude": float(lat) if lat and lat.strip() else None,
            "longitude": float(lon) if lon and lon.strip() else None,
            "city": city if city and city.strip() else None,
            "country": country if country and country.strip() else None
        }
    }
    
    try:
        # Call your /assist endpoint
        response = requests.post(
            f"{API_BASE}/assist", 
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Store data for map functionality
            last_analysis_data = data
            
            # Generate formatted summary
            summary = format_medical_assessment(data)
            
            # Generate hospital map HTML
            hospitals = data.get('nearest_hospitals', [])
            map_html = generate_hospital_map_html(hospitals)
            
            return summary, map_html
        else:
            return f"❌ Analysis failed: {response.status_code} - {response.text}", "<p>Analysis failed</p>"
            
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to medical analysis service. Please ensure the backend is running at http://127.0.0.1:8000", "<p>Connection failed</p>"
    except Exception as e:
        return f"❌ Error during analysis: {str(e)}", "<p>Error occurred</p>"

def format_medical_assessment(data):
    """Format the medical assessment response from your backend"""
    summary = ""
    
    # Main assessment info
    condition_type = data.get('condition_type', 'unknown').replace('_', ' ').title()
    severity = data.get('severity', 'unknown').upper()
    confidence = data.get('confidence', 0) * 100
    
    # Header with severity-based styling
    if severity in ['HIGH', 'CRITICAL']:
        summary += f"🚨 **URGENT MEDICAL ASSESSMENT** 🚨\n\n"
    else:
        summary += f"🏥 **Medical Assessment Results**\n\n"
    
    summary += f"**Condition Type:** {condition_type}\n"
    summary += f"**Severity Level:** {severity}\n"
    summary += f"**AI Confidence:** {confidence:.1f}%\n\n"
    
    # Red flags (critical warnings)
    red_flags = data.get('red_flags', [])
    if red_flags:
        summary += "⚠️ **Critical Warning Signs Detected:**\n"
        for flag in red_flags:
            summary += f"• {flag}\n"
        summary += "\n"
    
    # Recommended actions
    actions = data.get('recommended_actions', [])
    if actions:
        summary += "🚨 **Immediate Actions Required:**\n"
        for i, action in enumerate(actions, 1):
            summary += f"{i}. {action}\n"
        summary += "\n"
    
    # Self-care advice
    self_care = data.get('self_care_advice')
    if self_care:
        summary += f"🩹 **Self-Care Guidance:**\n{self_care}\n\n"
    
    # Nearest hospitals with enhanced mapping
    hospitals = data.get('nearest_hospitals', [])
    if hospitals:
        summary += "🏥 **Nearest Hospitals & Emergency Services:**\n\n"
        for i, hospital in enumerate(hospitals[:5], 1):  # Show top 5
            name = hospital.get('name', 'Unknown Hospital')
            rating = hospital.get('rating', 'N/A')
            address = hospital.get('address', 'Address not available')
            maps_url = hospital.get('maps_url', '#')
            
            # Calculate approximate distance if location data available
            location = hospital.get('location', {})
            lat = location.get('lat') if location else None
            lng = location.get('lng') if location else None
            
            summary += f"**{i}. {name}**"
            if rating != 'N/A':
                summary += f" ({rating}★)"
            if hospital.get('user_ratings_total'):
                summary += f" - {hospital['user_ratings_total']} reviews"
            summary += f"\n"
            
            summary += f"   📍 **Address:** {address}\n"
            
            # Add opening status if available
            if hospital.get('open_now') is not None:
                status = "🟢 Open Now" if hospital['open_now'] else "🔴 Closed"
                summary += f"   ⏰ **Status:** {status}\n"
            
            # Enhanced maps links
            if maps_url and maps_url != '#':
                summary += f"   🗺️ **[Open in Google Maps]({maps_url})**\n"
            
            # Add directions link if coordinates available
            if lat and lng:
                directions_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}"
                summary += f"   🧭 **[Get Directions]({directions_url})**\n"
                
                # Add call option if place_id available
                place_id = hospital.get('place_id')
                if place_id:
                    place_url = f"https://www.google.com/maps/search/?api=1&query=Google&query_place_id={place_id}"
                    summary += f"   📞 **[Hospital Details & Phone]({place_url})**\n"
            
            summary += "\n"
        
        # Add general emergency services map
        summary += "🚨 **Find More Emergency Services:**\n"
        summary += "🗺️ **[All Nearby Hospitals](https://www.google.com/maps/search/hospital+near+me)**\n"
        summary += "🚑 **[Urgent Care Centers](https://www.google.com/maps/search/urgent+care+near+me)**\n"
        summary += "🏥 **[Emergency Rooms](https://www.google.com/maps/search/emergency+room+near+me)**\n\n"
    
    # Weather context (if available)
    weather = data.get('weather_context')
    if weather:
        temp = weather.get('temp_c')
        desc = weather.get('description', '')
        if temp is not None:
            summary += f"🌡️ **Local Weather:** {temp}°C, {desc}\n"
            summary += "*(Weather conditions may affect your symptoms)*\n\n"
    
    # Emergency guidance based on severity
    if severity in ['HIGH', 'CRITICAL']:
        summary += "🚨 **EMERGENCY GUIDANCE:**\n"
        summary += "• Call 911 or go to the nearest emergency room immediately\n"
        summary += "• Do not drive yourself - call an ambulance or have someone drive you\n"
        summary += "• Bring a list of current medications and medical history\n\n"
    elif severity == 'MODERATE':
        summary += "⚠️ **Medical Attention Recommended:**\n"
        summary += "• Contact your healthcare provider today\n"
        summary += "• Consider urgent care if symptoms worsen\n"
        summary += "• Monitor symptoms closely\n\n"
    
    # Footer disclaimer
    summary += "---\n"
    summary += "💡 **Disclaimer:** This AI assessment provides guidance only and cannot replace professional medical advice. "
    summary += "Always consult healthcare professionals for medical decisions."
    
    return summary

def test_backend_connection():
    """Test if backend is accessible"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            return "✅ Backend connected successfully"
        else:
            return f"⚠️ Backend responded with status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to backend. Please start your backend server first."
    except Exception as e:
        return f"❌ Connection test failed: {e}"

# Create Gradio interface
with gr.Blocks(title="AI LifeSaver Pro", theme=gr.themes.Soft()) as demo:
    
    # Header
    gr.HTML("""
    <div style="text-align: center; background: linear-gradient(90deg, #2196F3, #21CBF3); 
                padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0;">🚑 AI LifeSaver Pro</h1>
        <p style="color: white; margin: 5px 0;">AI-Powered Emergency Medical Assessment with Location Services</p>
    </div>
    """)
    
    # Connection status
    with gr.Row():
        connection_status = gr.Textbox(
            label="🔗 Backend Connection Status",
            value="Click 'Test Connection' to check backend status",
            interactive=False
        )
        test_connection_btn = gr.Button("🔍 Test Connection", size="sm")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📝 Symptom Information")
            
            symptoms = gr.Textbox(
                label="Describe your symptoms in detail",
                placeholder="e.g., severe chest pain radiating to left arm, shortness of breath, sweating",
                lines=4
            )
            gr.Markdown("*Be as specific as possible - include location, intensity, duration, and triggers*")
            
            gr.Markdown("### 👤 Personal Information")
            with gr.Row():
                age = gr.Number(
                    label="Age",
                    value=None,
                    minimum=0,
                    maximum=120
                )
                gender = gr.Dropdown(
                    choices=["male", "female", "other"],
                    label="Gender",
                    value=None
                )
            gr.Markdown("*Your age and gender help with more accurate assessment*")
            
            gr.Markdown("### 📍 Location (for nearby hospitals)")
            with gr.Row():
                city = gr.Textbox(
                    label="City",
                    placeholder="e.g., New York"
                )
                country = gr.Textbox(
                    label="Country", 
                    placeholder="e.g., USA"
                )
            
            gr.Markdown("### 🎯 Precise Location (Optional)")
            gr.Markdown("*For exact hospital distances and weather context*")
            with gr.Row():
                lat = gr.Textbox(
                    label="Latitude",
                    placeholder="e.g., 40.7128"
                )
                lon = gr.Textbox(
                    label="Longitude",
                    placeholder="e.g., -74.0060"
                )
            
            analyze_btn = gr.Button("🔍 Analyze Symptoms", variant="primary", size="lg")
            
        with gr.Column(scale=2):
            gr.Markdown("### 📋 Medical Assessment Results")
            
            output_text = gr.Textbox(
                label="AI Medical Assessment",
                lines=25,
                max_lines=30,
                show_copy_button=True
            )
            gr.Markdown("*Detailed analysis will appear here*")
            
            with gr.Row():
                speak_btn = gr.Button("🔊 Listen to Assessment", variant="secondary")
                clear_btn = gr.Button("🗑️ Clear Results", variant="secondary")
            
            audio_out = gr.Audio(
                label="🎵 Text-to-Speech Audio",
                type="filepath",
                interactive=False
            )
            
            # Hospital Map Section
            with gr.Accordion("🗺️ Hospital Locations & Maps", open=False):
                map_info = gr.HTML(
                    label="Interactive Hospital Map",
                    value="<p>Hospital locations will appear here after analysis</p>"
                )
                
                with gr.Row():
                    show_hospitals_btn = gr.Button("🏥 Show All Hospitals", variant="secondary")
                    show_urgent_care_btn = gr.Button("🚑 Show Urgent Care", variant="secondary")
                    show_emergency_btn = gr.Button("🆘 Show Emergency Rooms", variant="secondary")
    
    # Emergency contacts section
    gr.HTML("""
    <div style="background: #ffebee; padding: 15px; border-radius: 8px; 
                border-left: 4px solid #f44336; margin: 20px 0;">
        <h3 style="margin-top: 0;">🚨 Emergency Contacts</h3>
        <p><strong>Emergency Services:</strong> 911</p>
        <p><strong>Poison Control:</strong> 1-800-222-1222</p>
        <p><strong>Crisis Text Line:</strong> Text HOME to 741741</p>
        <p><strong>Suicide Prevention Lifeline:</strong> 988</p>
    </div>
    """)
    
    # Medical disclaimer
    gr.HTML("""
    <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; 
                border-left: 4px solid #2196f3; margin-top: 20px;">
        <strong>⚕️ Medical Disclaimer:</strong> This AI tool provides assessment guidance and cannot replace professional medical advice. 
        In life-threatening emergencies, <strong>call 911 immediately</strong>. Always consult qualified healthcare professionals for medical decisions.
        The AI assessment is based on symptom patterns and should not be considered a definitive diagnosis.
    </div>
    """)
    
    # Event handlers
    analyze_btn.click(
        analyze_symptoms,
        inputs=[symptoms, age, gender, lat, lon, city, country],
        outputs=[output_text, map_info]
    )
    
    speak_btn.click(
        speak_text,
        inputs=output_text,
        outputs=audio_out
    )
    
    clear_btn.click(
        lambda: ("", None, "<p>Hospital locations will appear here after analysis</p>"),
        outputs=[output_text, audio_out, map_info]
    )
    
    test_connection_btn.click(
        test_backend_connection,
        outputs=connection_status
    )
    
    # Map button handlers
    show_hospitals_btn.click(
        show_general_hospitals,
        outputs=map_info
    )
    
    show_urgent_care_btn.click(
        show_urgent_care, 
        outputs=map_info
    )
    
    show_emergency_btn.click(
        show_emergency_rooms,
        outputs=map_info
    )
    
    # Example cases
    gr.Examples(
        examples=[
            ["Severe crushing chest pain radiating to left arm, shortness of breath, sweating, nausea", 
             55, "male", "40.7128", "-74.0060", "New York", "USA"],
            ["Sudden severe headache, neck stiffness, sensitivity to light, fever", 
             28, "female", "41.8781", "-87.6298", "Chicago", "USA"],
            ["Severe abdominal pain in lower right side, nausea, vomiting, fever", 
             22, "female", "34.0522", "-118.2437", "Los Angeles", "USA"],
            ["Sudden weakness on right side of body, difficulty speaking, facial drooping", 
             67, "male", "29.7604", "-95.3698", "Houston", "USA"],
            ["Severe allergic reaction, facial swelling, difficulty breathing, hives all over body", 
             34, "other", "25.7617", "-80.1918", "Miami", "USA"],
            ["High fever, severe cough with blood, chest pain, difficulty breathing", 
             42, "male", "47.6062", "-122.3321", "Seattle", "USA"]
        ],
        inputs=[symptoms, age, gender, lat, lon, city, country],
        label="📚 Example Medical Cases"
    )

if __name__ == "__main__":
    print("🚀 Starting AI LifeSaver Pro...")
    print("🔗 Backend should be running at: http://127.0.0.1:8000")
    print("📝 Ready for medical emergency assessment!")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,  # Create secure public link
        debug=True
    )
