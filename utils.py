"""
AI Crop Doctor - Utility Functions
Fixed to properly generate reports in selected language
"""

import base64
import requests
import tempfile
import time
from datetime import datetime
from typing import Tuple, Optional, Dict
from PIL import Image
import io
from gtts import gTTS
from openai import OpenAI
from config import *

class AudioProcessor:
    """Audio processing with language detection"""
    
    @staticmethod
    def transcribe_audio(audio_file) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Transcribe audio with automatic language detection"""
        try:
            headers = {'authorization': ASSEMBLY_AI_KEY, 'content-type': 'application/json'}
            
            # Upload audio
            audio_file.seek(0)
            audio_data = audio_file.read()
            
            upload_response = requests.post(
                f'{ASSEMBLY_AI_URL}/upload',
                headers={'authorization': ASSEMBLY_AI_KEY},
                data=audio_data
            )
            
            if upload_response.status_code != 200:
                return None, None, "Failed to upload audio"
            
            audio_url = upload_response.json()['upload_url']
            
            # Request transcription
            transcript_request = {
                'audio_url': audio_url,
                'language_detection': True,
                'punctuate': True,
                'format_text': True
            }
            
            transcript_response = requests.post(
                f'{ASSEMBLY_AI_URL}/transcript',
                json=transcript_request,
                headers=headers
            )
            
            if transcript_response.status_code != 200:
                return None, None, "Transcription failed"
            
            transcript_id = transcript_response.json()['id']
            
            # Poll for completion
            for _ in range(120):
                time.sleep(1)
                
                polling_response = requests.get(
                    f'{ASSEMBLY_AI_URL}/transcript/{transcript_id}',
                    headers={'authorization': ASSEMBLY_AI_KEY}
                )
                
                if polling_response.status_code != 200:
                    continue
                
                result = polling_response.json()
                status = result.get('status')
                
                if status == 'completed':
                    text = result.get('text', '')
                    detected_lang = result.get('language_code', 'en')
                    
                    if not text:
                        return None, None, "No speech detected"
                    
                    lang_mapping = {
                        'en': 'en', 'hi': 'hi', 'pa': 'pa', 'ur': 'ur',
                        'en_us': 'en', 'en_uk': 'en', 'en_au': 'en'
                    }
                    
                    our_lang_code = lang_mapping.get(detected_lang.lower(), 'en')
                    return text, our_lang_code, None
                    
                elif status == 'error':
                    return None, None, f"Error: {result.get('error', 'Unknown')}"
            
            return None, None, "Timeout"
            
        except Exception as e:
            return None, None, f"Error: {str(e)}"
    
    @staticmethod
    def text_to_speech(text: str, language: str = 'en') -> Tuple[Optional[str], Optional[str]]:
        """Convert text to speech"""
        try:
            lang_code = LANGUAGES.get(language, {}).get('tts', 'en')
            tts = gTTS(text=text, lang=lang_code, slow=False)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                return tmp_file.name, None
        except:
            return None, "TTS failed"

class EnhancedPlantDiseaseDetector:
    """Enhanced disease detection"""
    
    @staticmethod
    def detect_disease_advanced(image_file) -> Tuple[Optional[Dict], Optional[str]]:
        """Detect plant disease using Plant.id"""
        try:
            image_file.seek(0)
            image_bytes = image_file.read()
            img = Image.open(io.BytesIO(image_bytes))
            
            # Optimize image
            max_size = 2000
            if max(img.size) > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=95)
            img_base64 = base64.b64encode(buffer.getvalue()).decode('ascii')
            
            headers = {
                'Api-Key': PLANT_ID_API_KEY,
                'Content-Type': 'application/json'
            }
            
            data = {
                'images': [img_base64],
                'modifiers': ["crops_fast", "similar_images"],
                'plant_language': "en",
                'disease_details': ["common_names", "description", "treatment"]
            }
            
            response = requests.post(PLANT_ID_URL, json=data, headers=headers, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return EnhancedPlantDiseaseDetector._parse_response(result), None
            else:
                return None, f"API error: {response.status_code}"
                    
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    @staticmethod
    def _parse_response(api_response: Dict) -> Dict:
        """Parse Plant.id response"""
        try:
            health = api_response.get('health_assessment', {})
            is_healthy = health.get('is_healthy', False)
            
            result = {
                'is_healthy': is_healthy,
                'health_probability': health.get('is_healthy_probability', 0),
                'diseases': [],
                'plant_name': 'Unknown',
                'suggestions': []
            }
            
            # Get plant info
            suggestions = api_response.get('suggestions', [])
            if suggestions:
                result['plant_name'] = suggestions[0].get('plant_name', 'Unknown')
            
            # Get diseases
            diseases = health.get('diseases', [])
            
            for disease in diseases[:3]:
                disease_info = {
                    'name': disease.get('name', 'Unknown'),
                    'probability': disease.get('probability', 0)
                }
                
                details = disease.get('disease_details', {})
                disease_info['description'] = details.get('description', '')
                
                treatment = details.get('treatment', {})
                if isinstance(treatment, dict):
                    disease_info['chemical'] = treatment.get('chemical', [])
                    disease_info['biological'] = treatment.get('biological', [])
                
                result['diseases'].append(disease_info)
            
            if result['diseases']:
                primary = result['diseases'][0]
                result['disease_name'] = primary['name']
                result['confidence'] = primary['probability']
                result['description'] = primary.get('description', '')
                
                suggestions = []
                if 'chemical' in primary:
                    suggestions.extend(primary['chemical'][:3])
                if 'biological' in primary:
                    suggestions.extend(primary['biological'][:3])
                
                result['suggestions'] = suggestions
            elif is_healthy:
                result['disease_name'] = 'Healthy Plant'
                result['confidence'] = result['health_probability']
                result['description'] = 'Your plant appears healthy'
            
            return result
            
        except Exception as e:
            return {
                'disease_name': 'Detection Error',
                'confidence': 0,
                'description': f'Error: {str(e)}',
                'suggestions': []
            }

class AIAnalyzer:
    """AI analysis with proper language support"""
    
    @staticmethod
    def analyze_problem(voice_text: str, disease_info: Dict, district: str, selected_language: str = 'en') -> Tuple[Optional[str], Optional[str]]:
        """Generate analysis using AI in the SELECTED language"""
        try:
            disease_summary = f"""
Disease: {disease_info.get('disease_name', 'Unknown')}
Confidence: {disease_info.get('confidence', 0) * 100:.1f}%
Description: {disease_info.get('description', 'Not available')}
Plant: {disease_info.get('plant_name', 'Unknown')}
"""
            
            if disease_info.get('suggestions'):
                disease_summary += "\nTreatments:\n"
                for s in disease_info['suggestions']:
                    disease_summary += f"• {s}\n"
            
            # Get language specific instructions
            language_instructions = {
                'en': {
                    'name': 'English',
                    'instruction': 'You MUST respond ONLY in English language.',
                    'example': 'Example: "Your crop has nutrient deficiency..."'
                },
                'hi': {
                    'name': 'Hindi (Devanagari script)',
                    'instruction': 'आपको केवल हिंदी भाषा में देवनागरी लिपि में जवाब देना है। अंग्रेजी में बिल्कुल नहीं।',
                    'example': 'उदाहरण: "आपकी फसल में पोषक तत्वों की कमी है..."'
                },
                'pa': {
                    'name': 'Punjabi (Gurmukhi script)',
                    'instruction': 'ਤੁਹਾਨੂੰ ਸਿਰਫ਼ ਪੰਜਾਬੀ ਭਾਸ਼ਾ ਵਿੱਚ ਗੁਰਮੁਖੀ ਲਿਪੀ ਵਿੱਚ ਜਵਾਬ ਦੇਣਾ ਹੈ। ਅੰਗਰੇਜ਼ੀ ਵਿੱਚ ਬਿਲਕੁਲ ਨਹੀਂ।',
                    'example': 'ਉਦਾਹਰਨ: "ਤੁਹਾਡੀ ਫਸਲ ਵਿੱਚ ਪੋਸ਼ਕ ਤੱਤਾਂ ਦੀ ਕਮੀ ਹੈ..."'
                },
                'ur': {
                    'name': 'Urdu (Arabic script)',
                    'instruction': 'آپ کو صرف اردو زبان میں عربی رسم الخط میں جواب دینا ہے۔ انگریزی میں بالکل نہیں۔',
                    'example': 'مثال: "آپ کی فصل میں غذائی اجزاء کی کمی ہے..."'
                }
            }
            
            lang_info = language_instructions.get(selected_language, language_instructions['en'])
            
            # Create STRONG system message
            system_message = f"""You are an expert agricultural advisor for Punjab, India farmers.

CRITICAL LANGUAGE REQUIREMENT:
{lang_info['instruction']}

Language: {lang_info['name']}
{lang_info['example']}

IMPORTANT RULES:
1. Write your ENTIRE response in {lang_info['name']} ONLY
2. DO NOT use English words or sentences
3. Use proper script: {'Devanagari' if selected_language == 'hi' else 'Gurmukhi' if selected_language == 'pa' else 'Arabic' if selected_language == 'ur' else 'Latin'}
4. All headings, descriptions, and recommendations must be in {lang_info['name']}

This is MANDATORY. The farmer only understands {lang_info['name']}."""

            # Create user prompt
            if selected_language == 'hi':
                user_prompt = f"""किसान की समस्या का विश्लेषण करें और हिंदी में विस्तृत सलाह दें।

किसान की समस्या:
{voice_text}

रोग का विवरण:
{disease_summary}

स्थान: {district}, पंजाब

कृपया हिंदी में एक विस्तृत रिपोर्ट प्रदान करें जिसमें शामिल हो:

1. **समस्या की पहचान**
   - मुख्य समस्या का सारांश
   - रोग की पुष्टि

2. **तुरंत करने योग्य कार्य**
   - 3-4 जरूरी कदम

3. **उपचार योजना**
   - जैविक उपचार
   - रासायनिक उपचार
   - प्रयोग विधि

4. **रोकथाम के उपाय**
   - भविष्य के लिए सुझाव

5. **रिकवरी का समय**
   - सुधार की अवधि

पूरी रिपोर्ट हिंदी में लिखें।"""

            elif selected_language == 'pa':
                user_prompt = f"""ਕਿਸਾਨ ਦੀ ਸਮੱਸਿਆ ਦਾ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰੋ ਅਤੇ ਪੰਜਾਬੀ ਵਿੱਚ ਵਿਸਤ੍ਰਿਤ ਸਲਾਹ ਦਿਓ।

ਕਿਸਾਨ ਦੀ ਸਮੱਸਿਆ:
{voice_text}

ਬਿਮਾਰੀ ਦਾ ਵੇਰਵਾ:
{disease_summary}

ਸਥਾਨ: {district}, ਪੰਜਾਬ

ਕਿਰਪਾ ਕਰਕੇ ਪੰਜਾਬੀ ਵਿੱਚ ਇੱਕ ਵਿਸਤ੍ਰਿਤ ਰਿਪੋਰਟ ਪ੍ਰਦਾਨ ਕਰੋ ਜਿਸ ਵਿੱਚ ਸ਼ਾਮਲ ਹੋਵੇ:

1. **ਸਮੱਸਿਆ ਦੀ ਪਛਾਣ**
   - ਮੁੱਖ ਸਮੱਸਿਆ ਦਾ ਸਾਰ
   - ਬਿਮਾਰੀ ਦੀ ਪੁਸ਼ਟੀ

2. **ਤੁਰੰਤ ਕਰਨ ਯੋਗ ਕਾਰਵਾਈਆਂ**
   - 3-4 ਜ਼ਰੂਰੀ ਕਦਮ

3. **ਇਲਾਜ ਦੀ ਯੋਜਨਾ**
   - ਜੈਵਿਕ ਇਲਾਜ
   - ਰਸਾਇਣਕ ਇਲਾਜ
   - ਵਰਤੋਂ ਦੀ ਵਿਧੀ

4. **ਰੋਕਥਾਮ ਦੇ ਉਪਾਅ**
   - ਭਵਿੱਖ ਲਈ ਸੁਝਾਅ

5. **ਰਿਕਵਰੀ ਦਾ ਸਮਾਂ**
   - ਸੁਧਾਰ ਦੀ ਮਿਆਦ

ਪੂਰੀ ਰਿਪੋਰਟ ਪੰਜਾਬੀ ਵਿੱਚ ਲਿਖੋ।"""

            elif selected_language == 'ur':
                user_prompt = f"""کسان کے مسئلے کا تجزیہ کریں اور اردو میں تفصیلی مشورہ دیں۔

کسان کا مسئلہ:
{voice_text}

بیماری کی تفصیل:
{disease_summary}

مقام: {district}، پنجاب

براہ کرم اردو میں ایک تفصیلی رپورٹ فراہم کریں جس میں شامل ہو:

1. **مسئلے کی شناخت**
   - اہم مسئلے کا خلاصہ
   - بیماری کی تصدیق

2. **فوری کارروائی**
   - 3-4 ضروری اقدامات

3. **علاج کا منصوبہ**
   - نامیاتی علاج
   - کیمیائی علاج
   - استعمال کا طریقہ

4. **روک تھام کے اقدامات**
   - مستقبل کے لیے تجاویز

5. **بحالی کا وقت**
   - بہتری کی مدت

پوری رپورٹ اردو میں لکھیں۔"""

            else:  # English
                user_prompt = f"""Analyze this farming problem and provide detailed advice in English.

FARMER'S PROBLEM:
{voice_text}

DISEASE ANALYSIS:
{disease_summary}

LOCATION: {district}, Punjab

Provide a comprehensive report in English including:

1. **Problem Identification**
   - Summarize main issue
   - Confirm disease

2. **Immediate Actions**
   - 3-4 urgent steps

3. **Treatment Plan**
   - Organic treatment
   - Chemical treatment
   - Application method

4. **Prevention Measures**
   - Future suggestions

5. **Recovery Timeline**
   - Expected improvement period

Write entire report in English."""

            # Call AI with STRONG language enforcement
            try:
                client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)
                
                response = client.chat.completions.create(
                    model=OPENROUTER_MODEL,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=3000
                )
                
                generated_report = response.choices[0].message.content
                
                # Verify language - if English words detected in non-English report, use fallback
                if selected_language != 'en':
                    english_word_count = sum(1 for word in generated_report.split() if word.isascii() and len(word) > 3)
                    total_words = len(generated_report.split())
                    
                    # If more than 30% English words in non-English report, use fallback
                    if total_words > 0 and (english_word_count / total_words) > 0.3:
                        return AIAnalyzer._generate_fallback_report(voice_text, disease_info, district, selected_language), None
                
                return generated_report, None
                
            except Exception as e:
                return AIAnalyzer._generate_fallback_report(voice_text, disease_info, district, selected_language), None
                    
        except Exception as e:
            return AIAnalyzer._generate_fallback_report(voice_text, disease_info, district, selected_language), None
    
    @staticmethod
    def _generate_fallback_report(voice_text, disease_info, district, language):
        """Fallback report in selected language"""
        
        if language == 'hi':
            return f"""
**फसल स्वास्थ्य विश्लेषण रिपोर्ट**

**स्थान:** {district}, पंजाब
**समस्या का विवरण:** {voice_text}

**पहचानी गई बीमारी:** {disease_info.get('disease_name', 'अज्ञात')}
**विश्वास स्तर:** {disease_info.get('confidence', 0) * 100:.1f}%

**विवरण:** {disease_info.get('description', 'उपलब्ध नहीं')}

**तत्काल आवश्यक कार्य:**
1. प्रभावित पौधों को अलग करें
2. संक्रमित भागों को हटाएं और जलाएं
3. हवा का संचार बढ़ाएं
4. पानी देने की मात्रा समायोजित करें

**उपचार:**
"""+ '\n'.join(f"• {s}" for s in disease_info.get('suggestions', [])[:5]) + """

**रोकथाम:**
• नियमित निगरानी
• उचित दूरी
• फसल चक्र
• प्रतिरोधी किस्में

**रिकवरी समय:** 2-4 सप्ताह

**नोट:** गंभीर मामलों में स्थानीय कृषि विशेषज्ञ से परामर्श करें।
"""
        
        elif language == 'pa':
            return f"""
**ਫਸਲ ਸਿਹਤ ਵਿਸ਼ਲੇਸ਼ਣ ਰਿਪੋਰਟ**

**ਸਥਾਨ:** {district}, ਪੰਜਾਬ
**ਸਮੱਸਿਆ ਦਾ ਵੇਰਵਾ:** {voice_text}

**ਪਛਾਣੀ ਗਈ ਬਿਮਾਰੀ:** {disease_info.get('disease_name', 'ਅਣਜਾਣ')}
**ਵਿਸ਼ਵਾਸ ਪੱਧਰ:** {disease_info.get('confidence', 0) * 100:.1f}%

**ਵੇਰਵਾ:** {disease_info.get('description', 'ਉਪਲਬਧ ਨਹੀਂ')}

**ਤੁਰੰਤ ਜ਼ਰੂਰੀ ਕਾਰਵਾਈਆਂ:**
1. ਪ੍ਰਭਾਵਿਤ ਪੌਦਿਆਂ ਨੂੰ ਵੱਖ ਕਰੋ
2. ਸੰਕਰਮਿਤ ਹਿੱਸਿਆਂ ਨੂੰ ਹਟਾਓ ਅਤੇ ਸਾੜੋ
3. ਹਵਾ ਦਾ ਸੰਚਾਰ ਵਧਾਓ
4. ਪਾਣੀ ਦੇਣ ਦੀ ਮਾਤਰਾ ਨੂੰ ਠੀਕ ਕਰੋ

**ਇਲਾਜ:**
"""+ '\n'.join(f"• {s}" for s in disease_info.get('suggestions', [])[:5]) + """

**ਰੋਕਥਾਮ:**
• ਨਿਯਮਿਤ ਨਿਗਰਾਨੀ
• ਸਹੀ ਦੂਰੀ
• ਫਸਲ ਚੱਕਰ
• ਰੋਧਕ ਕਿਸਮਾਂ

**ਰਿਕਵਰੀ ਸਮਾਂ:** 2-4 ਹਫ਼ਤੇ

**ਨੋਟ:** ਗੰਭੀਰ ਮਾਮਲਿਆਂ ਵਿੱਚ ਸਥਾਨਕ ਖੇਤੀਬਾੜੀ ਮਾਹਿਰ ਨਾਲ ਸਲਾਹ ਕਰੋ।
"""
        
        elif language == 'ur':
            return f"""
**فصل صحت تجزیہ رپورٹ**

**مقام:** {district}، پنجاب
**مسئلے کی تفصیل:** {voice_text}

**شناخت شدہ بیماری:** {disease_info.get('disease_name', 'نامعلوم')}
**اعتماد کی سطح:** {disease_info.get('confidence', 0) * 100:.1f}%

**تفصیل:** {disease_info.get('description', 'دستیاب نہیں')}

**فوری ضروری اقدامات:**
1. متاثرہ پودوں کو الگ کریں
2. متاثرہ حصوں کو ہٹائیں اور جلائیں
3. ہوا کی گردش بڑھائیں
4. پانی دینے کی مقدار کو ایڈجسٹ کریں

**علاج:**
"""+ '\n'.join(f"• {s}" for s in disease_info.get('suggestions', [])[:5]) + """

**روک تھام:**
• باقاعدہ نگرانی
• مناسب فاصلہ
• فصل گردش
• مزاحم اقسام

**بحالی کا وقت:** 2-4 ہفتے

**نوٹ:** سنگین معاملات میں مقامی زرعی ماہر سے مشورہ کریں۔
"""
        
        else:  # English
            return f"""
**Crop Health Analysis Report**

**Location:** {district}, Punjab
**Problem Description:** {voice_text}

**Disease Detected:** {disease_info.get('disease_name', 'Unknown')}
**Confidence Level:** {disease_info.get('confidence', 0) * 100:.1f}%

**Description:** {disease_info.get('description', 'Not available')}

**Immediate Actions Required:**
1. Isolate affected plants
2. Remove and burn infected parts
3. Improve air circulation
4. Adjust watering schedule

**Treatment:**
"""+ '\n'.join(f"• {s}" for s in disease_info.get('suggestions', [])[:5]) + """

**Prevention:**
• Regular monitoring
• Proper spacing
• Crop rotation
• Resistant varieties

**Recovery Time:** 2-4 weeks

**Note:** Consult local agricultural expert for severe cases.
"""

def check_api_configuration():
    """Check API configuration"""
    status = {'all_configured': True, 'missing': []}
    
    if ASSEMBLY_AI_KEY == "your_assembly_ai_key_here":
        status['all_configured'] = False
        status['missing'].append('AssemblyAI')
    
    if PLANT_ID_API_KEY == "your_plant_id_api_key_here":
        status['all_configured'] = False
        status['missing'].append('Plant.id')
    
    if OPENROUTER_API_KEY == "your_openrouter_api_key_here":
        status['all_configured'] = False
        status['missing'].append('OpenRouter')
    
    return status

def validate_inputs(audio_file, image_file, district):
    """Validate inputs"""
    if not audio_file:
        return False, "Please upload audio file"
    if not image_file:
        return False, "Please upload plant image"
    if district == "Select District":
        return False, "Please select your district"
    return True, ""

def create_fallback_disease_info():
    """Create fallback disease info"""
    return {
        'disease_name': 'Manual inspection needed',
        'confidence': 0,
        'description': 'Unable to detect automatically',
        'suggestions': ['Consult local agricultural expert'],
        'is_healthy': False
    }

def generate_text_report(voice_text, disease_info, ai_report, district, language):
    """Generate downloadable report"""
    return f"""
{'='*70}
AI CROP DOCTOR - ANALYSIS REPORT
{'='*70}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Location: {district}, Punjab
Language: {language}

{'='*70}
VOICE INPUT:
{'='*70}
{voice_text}

{'='*70}
DISEASE DETECTION:
{'='*70}
Disease: {disease_info.get('disease_name', 'Unknown')}
Confidence: {disease_info.get('confidence', 0) * 100:.1f}%
Plant: {disease_info.get('plant_name', 'Unknown')}

{'='*70}
AI RECOMMENDATIONS:
{'='*70}
{ai_report}

{'='*70}
AI Crop Doctor v{APP_VERSION}
{'='*70}
"""