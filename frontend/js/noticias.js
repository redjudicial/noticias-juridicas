// Configuración de Supabase
const SUPABASE_URL = 'https://qfomiierchksyfhxoukj.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFmb21paWVyY2hrc3lmaHhvdWtqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEwMjgxNTYsImV4cCI6MjA2NjYwNDE1Nn0.HqlptdYXjd2s9q8xHEmgQPyf6a95fosb0YT5b4asMA8';

// Variables globales
let noticias = [];
let noticiasFiltradas = [];
let paginaActual = 1;
const noticiasPorPagina = 12;

// Elementos del DOM
const contenedorNoticias = document.getElementById('noticias-container');
const filtroFuente = document.getElementById('fuente-filter');
const ordenSelect = document.getElementById('orden-filter');
const buscador = document.getElementById('search-input');
const paginacion = document.getElementById('paginacion');
const loadingSpinner = document.getElementById('loading-spinner');
const totalNoticias = document.getElementById('total-noticias');
const ultimaActualizacion = document.getElementById('ultima-actualizacion');

// Inicializar la aplicación
document.addEventListener('DOMContentLoaded', function() {
    cargarNoticias();
    configurarEventos();
});

// Cargar noticias desde Supabase
async function cargarNoticias() {
    mostrarLoading(true);
    
    try {
        const response = await fetch(`${SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&order=fecha_publicacion.desc`, {
            headers: {
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Error al cargar noticias');
        }
        
        noticias = await response.json();
        noticiasFiltradas = [...noticias];
        
        // Aplicar ordenamiento por defecto (más recientes primero)
        aplicarOrdenamiento();
        
        actualizarEstadisticas();
        mostrarNoticias();
        
    } catch (error) {
        console.error('Error cargando noticias:', error);
        mostrarError('Error al cargar las noticias. Por favor, intente nuevamente.');
    } finally {
        mostrarLoading(false);
    }
}

// Configurar event listeners
function configurarEventos() {
    // Filtros
    if (filtroFuente) {
        filtroFuente.addEventListener('change', aplicarFiltros);
    }
    if (ordenSelect) {
        ordenSelect.addEventListener('change', aplicarOrdenamiento);
    }
    
    // Buscador con debounce
    if (buscador) {
        let timeoutBusqueda;
        buscador.addEventListener('input', function() {
            clearTimeout(timeoutBusqueda);
            timeoutBusqueda = setTimeout(aplicarFiltros, 300);
        });
    }
}

// Aplicar filtros
function aplicarFiltros() {
    const fuenteSeleccionada = filtroFuente ? filtroFuente.value : '';
    const terminoBusqueda = buscador ? buscador.value.toLowerCase() : '';
    
    noticiasFiltradas = noticias.filter(noticia => {
        // Filtro por fuente
        if (fuenteSeleccionada && noticia.fuente !== fuenteSeleccionada) {
            return false;
        }
        
        // Filtro por búsqueda
        if (terminoBusqueda) {
            const textoBusqueda = `${noticia.titulo} ${noticia.resumen_ejecutivo || ''} ${noticia.fuente}`.toLowerCase();
            if (!textoBusqueda.includes(terminoBusqueda)) {
                return false;
            }
        }
        
        return true;
    });
    
    paginaActual = 1;
    actualizarEstadisticas();
    mostrarNoticias();
}

// Aplicar ordenamiento
function aplicarOrdenamiento() {
    const orden = ordenSelect ? ordenSelect.value : 'fecha_desc';
    
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
    
    paginaActual = 1;
    mostrarNoticias();
}

// Mostrar noticias
function mostrarNoticias() {
    const inicio = (paginaActual - 1) * noticiasPorPagina;
    const fin = inicio + noticiasPorPagina;
    const noticiasPagina = noticiasFiltradas.slice(inicio, fin);
    
    if (noticiasPagina.length === 0) {
        contenedorNoticias.innerHTML = `
            <div class="no-noticias">
                <i class="fas fa-newspaper"></i>
                <h3>No se encontraron noticias</h3>
                <p>Intenta ajustar los filtros o vuelve más tarde.</p>
            </div>
        `;
        paginacion.innerHTML = '';
        return;
    }
    
    const noticiasHTML = noticiasPagina.map(noticia => crearElementoNoticia(noticia)).join('');
    contenedorNoticias.innerHTML = noticiasHTML;
    
    mostrarPaginacion();
}

// Crear elemento de noticia
function crearElementoNoticia(noticia) {
    // Usar fecha_actualizacion si existe, sino fecha_publicacion
    const fechaNoticia = noticia.fecha_actualizacion || noticia.fecha_publicacion;
    const fecha = new Date(fechaNoticia).toLocaleDateString('es-CL', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    const fuenteDisplay = getFuenteDisplayName(noticia.fuente);
    const resumen = noticia.resumen_ejecutivo || 'Sin resumen disponible';

    return `
        <article class="noticia">
            <div class="noticia-header">
                <div class="noticia-meta">
                    <span class="noticia-fuente">${fuenteDisplay}</span>
                    <span class="noticia-fecha">
                        <i class="far fa-calendar-alt"></i>
                        ${fecha}
                    </span>
                </div>
                <h3 class="noticia-titulo">
                    <a href="${noticia.url_origen}" target="_blank" rel="noopener noreferrer">
                        ${noticia.titulo}
                    </a>
                </h3>
            </div>
            <div class="noticia-contenido">
                <div class="noticia-resumen">
                    <p>${resumen}</p>
                </div>
                <div class="noticia-footer">
                    <a href="${noticia.url_origen}" target="_blank" rel="noopener noreferrer" class="btn-ver-mas">
                        <i class="fas fa-external-link-alt"></i>
                        Leer más
                    </a>
                </div>
            </div>
        </article>
    `;
}

// Mostrar paginación
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

// Cambiar página
function cambiarPagina(pagina) {
    paginaActual = pagina;
    mostrarNoticias();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Actualizar estadísticas
function actualizarEstadisticas() {
    const total = noticias.length;
    const filtradas = noticiasFiltradas.length;
    
    if (totalNoticias) {
        totalNoticias.textContent = filtradas;
    }
    if (ultimaActualizacion) {
        ultimaActualizacion.textContent = `Última actualización: ${new Date().toLocaleTimeString('es-CL')}`;
    }
}

// Mostrar/ocultar loading
function mostrarLoading(mostrar) {
    if (mostrar) {
        loadingSpinner.style.display = 'block';
        contenedorNoticias.style.opacity = '0.5';
    } else {
        loadingSpinner.style.display = 'none';
        contenedorNoticias.style.opacity = '1';
    }
}

// Mostrar error
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

// Obtener nombre de fuente para mostrar
function getFuenteDisplayName(fuente) {
    const fuentes = {
        'poder_judicial': 'Poder Judicial',
        'contraloria': 'Contraloría',
        'tdpi': 'Tribunal de Propiedad Industrial',
        'cde': 'Consejo de Defensa del Estado',
        'tdlc': 'Tribunal de Defensa de la Libre Competencia',
        '1ta': 'Tribunal Ambiental',
        '3ta': 'Tribunal Ambiental',
        'tribunal_ambiental': 'Tribunal Ambiental',
        'ministerio_justicia': 'Ministerio de Justicia'
    };
    return fuentes[fuente] || fuente;
}

// Exportar funciones para uso global
window.cambiarPagina = cambiarPagina; 