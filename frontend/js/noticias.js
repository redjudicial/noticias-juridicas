// Configuración de Supabase
const SUPABASE_URL = 'https://your-project.supabase.co';
const SUPABASE_KEY = 'your-anon-key';

// Variables globales
let noticias = [];
let noticiasFiltradas = [];
let paginaActual = 1;
const noticiasPorPagina = 10;
let ordenActual = 'fecha_desc'; // Por defecto: más recientes primero

// Elementos del DOM
const contenedorNoticias = document.getElementById('noticias-container');
const filtroFuente = document.getElementById('filtro-fuente');
const filtroCategoria = document.getElementById('filtro-categoria');
const ordenSelect = document.getElementById('orden-select');
const buscador = document.getElementById('buscador');
const paginacion = document.getElementById('paginacion');
const loadingSpinner = document.getElementById('loading-spinner');
const estadisticas = document.getElementById('estadisticas');

// Inicializar la aplicación
document.addEventListener('DOMContentLoaded', function() {
    inicializarFiltros();
    cargarNoticias();
    configurarEventos();
});

function inicializarFiltros() {
    // Configurar opciones de ordenamiento
    ordenSelect.innerHTML = `
        <option value="fecha_desc">Más recientes primero</option>
        <option value="fecha_asc">Más antiguos primero</option>
        <option value="titulo_asc">Título A-Z</option>
        <option value="titulo_desc">Título Z-A</option>
        <option value="fuente_asc">Fuente A-Z</option>
        <option value="relevancia_desc">Más relevantes</option>
    `;
}

async function cargarNoticias() {
    mostrarLoading(true);
    
    try {
        // Cargar desde Supabase con ordenamiento por fecha/hora
        const response = await fetch(`${SUPABASE_URL}/rest/v1/noticias_juridicas`, {
            method: 'GET',
            headers: {
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Error al cargar noticias');
        }
        
        noticias = await response.json();
        
        // Ordenar por fecha de publicación (más recientes primero)
        noticias.sort((a, b) => {
            const fechaA = new Date(a.fecha_publicacion);
            const fechaB = new Date(b.fecha_publicacion);
            return fechaB - fechaA; // Descendente (más reciente primero)
        });
        
        noticiasFiltradas = [...noticias];
        actualizarEstadisticas();
        mostrarNoticias();
        
    } catch (error) {
        console.error('Error cargando noticias:', error);
        mostrarError('Error al cargar las noticias. Por favor, intente nuevamente.');
    } finally {
        mostrarLoading(false);
    }
}

function configurarEventos() {
    // Filtros
    filtroFuente.addEventListener('change', aplicarFiltros);
    filtroCategoria.addEventListener('change', aplicarFiltros);
    ordenSelect.addEventListener('change', aplicarOrdenamiento);
    
    // Buscador con debounce
    let timeoutBusqueda;
    buscador.addEventListener('input', function() {
        clearTimeout(timeoutBusqueda);
        timeoutBusqueda = setTimeout(aplicarFiltros, 300);
    });
}

function aplicarFiltros() {
    const fuenteSeleccionada = filtroFuente.value;
    const categoriaSeleccionada = filtroCategoria.value;
    const terminoBusqueda = buscador.value.toLowerCase();
    
    noticiasFiltradas = noticias.filter(noticia => {
        // Filtro por fuente
        if (fuenteSeleccionada && fuenteSeleccionada !== 'todas' && 
            noticia.fuente !== fuenteSeleccionada) {
            return false;
        }
        
        // Filtro por categoría
        if (categoriaSeleccionada && categoriaSeleccionada !== 'todas' && 
            noticia.categoria !== categoriaSeleccionada) {
            return false;
        }
        
        // Filtro por búsqueda
        if (terminoBusqueda) {
            const textoBusqueda = `${noticia.titulo} ${noticia.resumen_ejecutivo || ''} ${noticia.cuerpo_completo || ''}`.toLowerCase();
            if (!textoBusqueda.includes(terminoBusqueda)) {
                return false;
            }
        }
        
        return true;
    });
    
    // Aplicar ordenamiento actual
    aplicarOrdenamiento();
    
    paginaActual = 1;
    actualizarEstadisticas();
    mostrarNoticias();
}

function aplicarOrdenamiento() {
    const orden = ordenSelect.value;
    
    noticiasFiltradas.sort((a, b) => {
        switch (orden) {
            case 'fecha_desc':
                return new Date(b.fecha_publicacion) - new Date(a.fecha_publicacion);
            case 'fecha_asc':
                return new Date(a.fecha_publicacion) - new Date(b.fecha_publicacion);
            case 'titulo_asc':
                return a.titulo.localeCompare(b.titulo);
            case 'titulo_desc':
                return b.titulo.localeCompare(a.titulo);
            case 'fuente_asc':
                return a.fuente.localeCompare(b.fuente);
            case 'relevancia_desc':
                return (b.relevancia_juridica || 0) - (a.relevancia_juridica || 0);
            default:
                return new Date(b.fecha_publicacion) - new Date(a.fecha_publicacion);
        }
    });
    
    mostrarNoticias();
}

function mostrarNoticias() {
    const inicio = (paginaActual - 1) * noticiasPorPagina;
    const fin = inicio + noticiasPorPagina;
    const noticiasPagina = noticiasFiltradas.slice(inicio, fin);
    
    contenedorNoticias.innerHTML = '';
    
    if (noticiasPagina.length === 0) {
        contenedorNoticias.innerHTML = `
            <div class="no-resultados">
                <i class="fas fa-search"></i>
                <h3>No se encontraron noticias</h3>
                <p>Intente ajustar los filtros o términos de búsqueda.</p>
            </div>
        `;
        return;
    }
    
    noticiasPagina.forEach(noticia => {
        const noticiaElement = crearElementoNoticia(noticia);
        contenedorNoticias.appendChild(noticiaElement);
    });
    
    mostrarPaginacion();
}

function crearElementoNoticia(noticia) {
    const fecha = new Date(noticia.fecha_publicacion);
    const fechaFormateada = fecha.toLocaleDateString('es-CL', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    // Usar resumen ejecutivo si está disponible, sino usar extracto del contenido
    const resumen = noticia.resumen_ejecutivo || 
                   noticia.extracto_fuente || 
                   noticia.cuerpo_completo?.substring(0, 200) + '...' || 
                   'Resumen no disponible';
    
    // Mostrar título completo
    const tituloCompleto = noticia.titulo || 'Sin título';
    
    // Determinar clase de relevancia
    const relevancia = noticia.relevancia_juridica || 0;
    const claseRelevancia = relevancia >= 4 ? 'alta-relevancia' : 
                           relevancia >= 2 ? 'media-relevancia' : 'baja-relevancia';
    
    const elemento = document.createElement('article');
    elemento.className = `noticia ${claseRelevancia}`;
    elemento.innerHTML = `
        <div class="noticia-header">
            <div class="noticia-meta">
                <span class="noticia-fuente">${noticia.fuente}</span>
                <span class="noticia-fecha">${fechaFormateada}</span>
                ${noticia.categoria ? `<span class="noticia-categoria">${noticia.categoria}</span>` : ''}
                ${relevancia > 0 ? `<span class="noticia-relevancia">⭐ ${relevancia}</span>` : ''}
            </div>
            <h2 class="noticia-titulo">
                <a href="${noticia.url_origen}" target="_blank" rel="noopener noreferrer">
                    ${tituloCompleto}
                </a>
            </h2>
        </div>
        
        <div class="noticia-contenido">
            <div class="noticia-resumen">
                <p>${resumen}</p>
            </div>
            
            ${noticia.palabras_clave && noticia.palabras_clave.length > 0 ? `
                <div class="noticia-etiquetas">
                    ${noticia.palabras_clave.slice(0, 5).map(palabra => 
                        `<span class="etiqueta">${palabra}</span>`
                    ).join('')}
                </div>
            ` : ''}
        </div>
        
        <div class="noticia-footer">
            <a href="${noticia.url_origen}" target="_blank" rel="noopener noreferrer" class="btn-ver-mas">
                <i class="fas fa-external-link-alt"></i>
                Ver noticia completa
            </a>
            ${noticia.url_imagen ? `
                <a href="${noticia.url_imagen}" target="_blank" class="btn-imagen">
                    <i class="fas fa-image"></i>
                    Ver imagen
                </a>
            ` : ''}
        </div>
    `;
    
    return elemento;
}

function mostrarPaginacion() {
    const totalPaginas = Math.ceil(noticiasFiltradas.length / noticiasPorPagina);
    
    if (totalPaginas <= 1) {
        paginacion.innerHTML = '';
        return;
    }
    
    let paginacionHTML = '<div class="paginacion">';
    
    // Botón anterior
    if (paginaActual > 1) {
        paginacionHTML += `<button onclick="cambiarPagina(${paginaActual - 1})" class="btn-pagina">
            <i class="fas fa-chevron-left"></i> Anterior
        </button>`;
    }
    
    // Números de página
    const inicio = Math.max(1, paginaActual - 2);
    const fin = Math.min(totalPaginas, paginaActual + 2);
    
    for (let i = inicio; i <= fin; i++) {
        const clase = i === paginaActual ? 'btn-pagina activa' : 'btn-pagina';
        paginacionHTML += `<button onclick="cambiarPagina(${i})" class="${clase}">${i}</button>`;
    }
    
    // Botón siguiente
    if (paginaActual < totalPaginas) {
        paginacionHTML += `<button onclick="cambiarPagina(${paginaActual + 1})" class="btn-pagina">
            Siguiente <i class="fas fa-chevron-right"></i>
        </button>`;
    }
    
    paginacionHTML += '</div>';
    paginacion.innerHTML = paginacionHTML;
}

function cambiarPagina(pagina) {
    paginaActual = pagina;
    mostrarNoticias();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function actualizarEstadisticas() {
    const total = noticias.length;
    const filtradas = noticiasFiltradas.length;
    
    estadisticas.innerHTML = `
        <div class="estadisticas">
            <span class="estadistica">
                <i class="fas fa-newspaper"></i>
                Total: ${total.toLocaleString()}
            </span>
            <span class="estadistica">
                <i class="fas fa-filter"></i>
                Mostrando: ${filtradas.toLocaleString()}
            </span>
            ${filtradas < total ? `
                <span class="estadistica filtros-activos">
                    <i class="fas fa-info-circle"></i>
                    Filtros activos
                </span>
            ` : ''}
        </div>
    `;
}

function mostrarLoading(mostrar) {
    if (mostrar) {
        loadingSpinner.style.display = 'flex';
        contenedorNoticias.style.opacity = '0.5';
    } else {
        loadingSpinner.style.display = 'none';
        contenedorNoticias.style.opacity = '1';
    }
}

function mostrarError(mensaje) {
    contenedorNoticias.innerHTML = `
        <div class="error-mensaje">
            <i class="fas fa-exclamation-triangle"></i>
            <h3>Error</h3>
            <p>${mensaje}</p>
            <button onclick="cargarNoticias()" class="btn-reintentar">
                <i class="fas fa-redo"></i>
                Reintentar
            </button>
        </div>
    `;
}

// Función para actualizar filtros dinámicamente
function actualizarFiltros() {
    const fuentes = [...new Set(noticias.map(n => n.fuente))].sort();
    const categorias = [...new Set(noticias.map(n => n.categoria).filter(Boolean))].sort();
    
    // Actualizar filtro de fuentes
    filtroFuente.innerHTML = '<option value="todas">Todas las fuentes</option>';
    fuentes.forEach(fuente => {
        filtroFuente.innerHTML += `<option value="${fuente}">${fuente}</option>`;
    });
    
    // Actualizar filtro de categorías
    filtroCategoria.innerHTML = '<option value="todas">Todas las categorías</option>';
    categorias.forEach(categoria => {
        filtroCategoria.innerHTML += `<option value="${categoria}">${categoria}</option>`;
    });
}

// Función para limpiar filtros
function limpiarFiltros() {
    filtroFuente.value = 'todas';
    filtroCategoria.value = 'todas';
    ordenSelect.value = 'fecha_desc';
    buscador.value = '';
    aplicarFiltros();
}

// Exportar funciones para uso global
window.cambiarPagina = cambiarPagina;
window.limpiarFiltros = limpiarFiltros; 