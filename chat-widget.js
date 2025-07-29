// chat-widget.js - Versión simplificada y arreglada
console.log('🔧 Chat widget iniciando...');

  // Configuración
const WIDGET_COLOR = '#1a365d';
  const BUTTON_TEXT = '¿Tienes dudas? Chatea con Red Judicial';
  const API_URL = '/api/chat';

  // Crear burbuja
  const bubble = document.createElement('button');
  bubble.className = 'rj-chat-bubble';
  bubble.innerHTML = `
    <span class="rj-chat-icon"><i class="fas fa-robot"></i></span>
    <span class="rj-chat-badge" id="rj-chat-badge">Nuevo</span>
  `;
  bubble.title = BUTTON_TEXT;

console.log('✅ Burbuja creada:', bubble);
console.log('✅ HTML de la burbuja:', bubble.innerHTML);

  document.body.appendChild(bubble);

console.log('✅ Burbuja agregada al DOM');
console.log('✅ Elemento en DOM:', document.querySelector('.rj-chat-bubble'));

// Verificar si el elemento es visible
setTimeout(() => {
  const rect = bubble.getBoundingClientRect();
  console.log('✅ Posición del elemento:', rect);
  console.log('✅ ¿Elemento visible?', rect.width > 0 && rect.height > 0);
  console.log('✅ Display style:', window.getComputedStyle(bubble).display);
  console.log('✅ Visibility style:', window.getComputedStyle(bubble).visibility);
  console.log('✅ Opacity style:', window.getComputedStyle(bubble).opacity);
}, 1000);

  // Crear modal (inicialmente oculto)
  let modal = null;
  let chatBody = null;
  let chatInput = null;
  let chatSend = null;
  let threadId = null;

  function openModal() {
    if (modal) return;
    modal = document.createElement('div');
    modal.className = 'rj-chat-modal';
    modal.innerHTML = `
      <button class="rj-chat-close" title="Cerrar">&times;</button>
      <div class="rj-chat-body"></div>
      <form class="rj-chat-footer">
        <input class="rj-chat-input" type="text" placeholder="Escribe tu pregunta..." autocomplete="off" required />
        <button class="rj-chat-send" type="submit">Enviar</button>
      </form>
    `;
    document.body.appendChild(modal);
    chatBody = modal.querySelector('.rj-chat-body');
    chatInput = modal.querySelector('.rj-chat-input');
    chatSend = modal.querySelector('.rj-chat-send');
    // Cerrar
    modal.querySelector('.rj-chat-close').onclick = closeModal;
    // Enviar mensaje
    modal.querySelector('.rj-chat-footer').onsubmit = sendMessage;
    chatInput.focus();
    // Mensaje inicial por defecto
    addMessage('Hola, ¿en qué te puedo ayudar?', 'assistant');
    
    // Agregar información de planes de estudiantes al contexto del chat
    const studentPlansInfo = `
    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0; font-size: 14px;">
      <strong>📚 Planes para Estudiantes de Derecho:</strong><br>
      <strong>🆓 Plan Gratis:</strong> Apuntes explicativos, foros, grupos especializados, noticias legales, webinars generales, normas legales (búsqueda relacional)<br>
      <strong>⭐ Plan Plus ($4.990/mes):</strong> Todo lo gratis + base semántica avanzada, simuladores de exámenes (uso limitado), normas legales (búsqueda semántica avanzada), ranking de estudiantes destacados, casos prácticos con corrección guiada<br>
      <strong>👑 Plan Elite ($9.990/mes):</strong> Todo lo Plus + red nacional de procuradores, simuladores sin límite, base semántica ilimitada en todas las materias, acceso preferente a recursos exclusivos, certificaciones especiales
    </div>
    `;
    chatBody.innerHTML += studentPlansInfo;
  }

  function closeModal() {
    if (modal) {
      modal.remove();
      modal = null;
      chatBody = null;
      chatInput = null;
      chatSend = null;
    }
  }

  bubble.onclick = openModal;

  // Animación del botón cada 15 segundos
  function animateBubble() {
    bubble.style.animation = 'none';
    bubble.offsetHeight; // Trigger reflow
    bubble.style.animation = 'rj-bounce-in 1.5s ease-out';
  }
  
  // Iniciar animación cada 15 segundos
  setInterval(animateBubble, 15000);

  // Lógica de chat
  async function sendMessage(e) {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if (!msg) return;
    addMessage(msg, 'user');
    chatInput.value = '';
    chatInput.disabled = true;
    chatSend.disabled = true;
    try {
      const resp = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, threadId })
      });
      const data = await resp.json();
      if (data.reply) {
        addMessage(data.reply, 'assistant');
        threadId = data.threadId;
      } else {
        addMessage('Lo siento, hubo un error. Intenta de nuevo más tarde.', 'assistant');
      }
    } catch (err) {
      addMessage('Lo siento, hubo un error de conexión.', 'assistant');
    }
    chatInput.disabled = false;
    chatSend.disabled = false;
    chatInput.focus();
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  function addMessage(text, who) {
    if (!chatBody) return;
    const msg = document.createElement('div');
    msg.className = 'rj-chat-msg ' + who;
    msg.textContent = text;
    chatBody.appendChild(msg);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  // Lógica para mostrar el badge solo si hay mensajes no leídos
  function setChatBadge(visible) {
    const badge = document.getElementById('rj-chat-badge');
    if (badge) badge.style.display = visible ? 'block' : 'none';
  }
  // Por defecto oculto, pero puedes llamar setChatBadge(true) cuando detectes mensajes no leídos
  setChatBadge(false);

console.log('✅ Chat widget inicializado completamente'); 