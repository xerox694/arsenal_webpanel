# 🧠 Arsenal V4 Ultimate - AI Unifié (OpenAI + Gemini)

import os
import asyncio
from typing import Optional, Dict, Any, List
from config import ArsenalConfig

# ==================== IMPORTS CONDITIONNELS ====================

# OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Gemini (Google)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class AIUltimate:
    """Gestionnaire AI unifié supportant OpenAI et Gemini"""
    
    def __init__(self):
        self.config = ArsenalConfig.AI_CONFIG
        self.openai_client = None
        self.gemini_model = None
        
        # Initialiser les clients disponibles
        self._init_openai()
        self._init_gemini()
        
        # Déterminer le provider par défaut
        self.default_provider = self._get_default_provider()
        
        print(f"🧠 AI Ultimate initialisé:")
        print(f"  - OpenAI: {'✅' if self.openai_available else '❌'}")
        print(f"  - Gemini: {'✅' if self.gemini_available else '❌'}")
        print(f"  - Provider par défaut: {self.default_provider}")
    
    def _init_openai(self):
        """Initialiser OpenAI si disponible"""
        if OPENAI_AVAILABLE and self.config.get('openai_api_key'):
            try:
                openai.api_key = self.config['openai_api_key']
                self.openai_client = openai.OpenAI(api_key=self.config['openai_api_key'])
                print("✅ OpenAI initialisé")
            except Exception as e:
                print(f"❌ Erreur initialisation OpenAI: {e}")
    
    def _init_gemini(self):
        """Initialiser Gemini si disponible"""
        if GEMINI_AVAILABLE and self.config.get('gemini_api_key'):
            try:
                genai.configure(api_key=self.config['gemini_api_key'])
                self.gemini_model = genai.GenerativeModel(self.config.get('gemini_model', 'gemini-pro'))
                print("✅ Gemini initialisé")
            except Exception as e:
                print(f"❌ Erreur initialisation Gemini: {e}")
    
    def _get_default_provider(self) -> str:
        """Déterminer le provider par défaut"""
        if self.gemini_available:
            return 'gemini'
        elif self.openai_available:
            return 'openai'
        else:
            return 'none'
    
    @property
    def openai_available(self) -> bool:
        """Vérifier si OpenAI est disponible"""
        return self.openai_client is not None
    
    @property
    def gemini_available(self) -> bool:
        """Vérifier si Gemini est disponible"""
        return self.gemini_model is not None
    
    @property
    def is_available(self) -> bool:
        """Vérifier si au moins un provider AI est disponible"""
        return self.openai_available or self.gemini_available
    
    async def chat(self, 
                   message: str, 
                   provider: Optional[str] = None,
                   system_prompt: Optional[str] = None,
                   max_tokens: Optional[int] = None,
                   temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        Chat unifié avec le provider spécifié ou par défaut
        
        Args:
            message: Message utilisateur
            provider: 'openai', 'gemini' ou None (défaut)
            system_prompt: Instructions système (optionnel)
            max_tokens: Limite de tokens (optionnel)
            temperature: Créativité 0-1 (optionnel)
        
        Returns:
            Dict avec 'response', 'provider', 'tokens_used', etc.
        """
        
        # Déterminer le provider à utiliser
        if provider is None:
            provider = self.default_provider
        
        if provider == 'none' or not self.is_available:
            return {
                'success': False,
                'error': 'Aucun provider AI disponible',
                'provider': 'none'
            }
        
        # Paramètres par défaut
        max_tokens = max_tokens or self.config.get('max_tokens', 2000)
        temperature = temperature or self.config.get('temperature', 0.7)
        
        try:
            if provider == 'gemini' and self.gemini_available:
                return await self._chat_gemini(message, system_prompt, max_tokens, temperature)
            elif provider == 'openai' and self.openai_available:
                return await self._chat_openai(message, system_prompt, max_tokens, temperature)
            else:
                # Fallback vers l'autre provider
                if self.gemini_available:
                    return await self._chat_gemini(message, system_prompt, max_tokens, temperature)
                elif self.openai_available:
                    return await self._chat_openai(message, system_prompt, max_tokens, temperature)
                else:
                    return {
                        'success': False,
                        'error': f'Provider {provider} non disponible',
                        'provider': provider
                    }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur AI: {str(e)}',
                'provider': provider
            }
    
    async def _chat_openai(self, message: str, system_prompt: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """Chat avec OpenAI"""
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        
        response = await asyncio.to_thread(
            self.openai_client.chat.completions.create,
            model=self.config.get('openai_model', 'gpt-3.5-turbo'),
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return {
            'success': True,
            'response': response.choices[0].message.content,
            'provider': 'openai',
            'model': self.config.get('openai_model', 'gpt-3.5-turbo'),
            'tokens_used': response.usage.total_tokens,
            'tokens_prompt': response.usage.prompt_tokens,
            'tokens_completion': response.usage.completion_tokens
        }
    
    async def _chat_gemini(self, message: str, system_prompt: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """Chat avec Gemini"""
        
        # Construire le prompt complet
        full_prompt = message
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{message}"
        
        # Configuration de génération
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature
        )
        
        response = await asyncio.to_thread(
            self.gemini_model.generate_content,
            full_prompt,
            generation_config=generation_config
        )
        
        return {
            'success': True,
            'response': response.text,
            'provider': 'gemini',
            'model': self.config.get('gemini_model', 'gemini-pro'),
            'tokens_used': response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
            'tokens_prompt': response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
            'tokens_completion': response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0
        }
    
    async def analyze_image(self, image_url: str, prompt: str = "Décris cette image") -> Dict[str, Any]:
        """Analyser une image (Gemini uniquement pour l'instant)"""
        
        if not self.gemini_available:
            return {
                'success': False,
                'error': 'Analyse d\'image nécessite Gemini',
                'provider': 'none'
            }
        
        try:
            # Pour Gemini Vision
            model = genai.GenerativeModel('gemini-pro-vision')
            
            response = await asyncio.to_thread(
                model.generate_content,
                [prompt, {"mime_type": "image/jpeg", "data": image_url}]
            )
            
            return {
                'success': True,
                'response': response.text,
                'provider': 'gemini',
                'model': 'gemini-pro-vision',
                'type': 'image_analysis'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur analyse image: {str(e)}',
                'provider': 'gemini'
            }
    
    def get_providers_status(self) -> Dict[str, Any]:
        """Obtenir le statut de tous les providers"""
        return {
            'openai': {
                'available': self.openai_available,
                'model': self.config.get('openai_model', 'gpt-3.5-turbo') if self.openai_available else None
            },
            'gemini': {
                'available': self.gemini_available,
                'model': self.config.get('gemini_model', 'gemini-pro') if self.gemini_available else None
            },
            'default_provider': self.default_provider,
            'enabled': self.is_available
        }
    
    async def translate_text(self, text: str, target_language: str = 'fr', provider: str = None) -> Dict[str, Any]:
        """Traduire du texte"""
        
        system_prompt = f"Tu es un traducteur expert. Traduis le texte suivant en {target_language}. Réponds uniquement avec la traduction, sans explication."
        
        return await self.chat(
            message=f"Traduis ce texte: {text}",
            provider=provider,
            system_prompt=system_prompt
        )
    
    async def generate_code(self, description: str, language: str = 'python', provider: str = None) -> Dict[str, Any]:
        """Générer du code"""
        
        system_prompt = f"Tu es un expert en programmation {language}. Génère du code propre, commenté et fonctionnel."
        
        return await self.chat(
            message=f"Génère du code {language} pour: {description}",
            provider=provider,
            system_prompt=system_prompt
        )

# ==================== INSTANCE GLOBALE ====================

# Instance globale du gestionnaire AI
ai_ultimate = AIUltimate()

# ==================== FONCTIONS UTILITAIRES ====================

async def quick_chat(message: str, provider: str = None) -> str:
    """Chat rapide qui retourne directement la réponse"""
    result = await ai_ultimate.chat(message, provider)
    return result.get('response', 'Erreur AI') if result.get('success') else f"Erreur: {result.get('error', 'Inconnue')}"

async def quick_translate(text: str, target: str = 'fr') -> str:
    """Traduction rapide"""
    result = await ai_ultimate.translate_text(text, target)
    return result.get('response', text) if result.get('success') else text

# ==================== TESTS ====================

async def test_ai_providers():
    """Tester tous les providers AI disponibles"""
    print("🧪 Test des providers AI...")
    
    test_message = "Bonjour! Comment allez-vous?"
    
    # Test OpenAI
    if ai_ultimate.openai_available:
        print("Testing OpenAI...")
        result = await ai_ultimate.chat(test_message, provider='openai')
        print(f"OpenAI: {result.get('success', False)} - {result.get('response', result.get('error'))[:100]}...")
    
    # Test Gemini
    if ai_ultimate.gemini_available:
        print("Testing Gemini...")
        result = await ai_ultimate.chat(test_message, provider='gemini')
        print(f"Gemini: {result.get('success', False)} - {result.get('response', result.get('error'))[:100]}...")
    
    # Test par défaut
    print("Testing default provider...")
    result = await ai_ultimate.chat(test_message)
    print(f"Default: {result.get('success', False)} - {result.get('response', result.get('error'))[:100]}...")

if __name__ == "__main__":
    # Test si lancé directement
    asyncio.run(test_ai_providers())
