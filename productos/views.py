from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Sum, Count
from .models import Producto, Categoria
from .forms import ProductoForm, CategoriaForm, BusquedaProductoForm


# ─────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────

def dashboard(request):
    """Vista principal con estadísticas generales."""
    total_productos = Producto.objects.count()
    productos_activos = Producto.objects.filter(estado='activo').count()
    productos_sin_stock = Producto.objects.filter(stock=0).count()
    total_categorias = Categoria.objects.count()
    valor_inventario = Producto.objects.aggregate(
        total=Sum('precio')
    )['total'] or 0

    productos_recientes = Producto.objects.select_related('categoria').order_by('-creado_en')[:5]

    context = {
        'total_productos': total_productos,
        'productos_activos': productos_activos,
        'productos_sin_stock': productos_sin_stock,
        'total_categorias': total_categorias,
        'valor_inventario': valor_inventario,
        'productos_recientes': productos_recientes,
    }
    return render(request, 'productos/dashboard.html', context)


# ─────────────────────────────────────────────
#  PRODUCTOS — CRUD
# ─────────────────────────────────────────────

def producto_lista(request):
    """Lista de productos con búsqueda y filtros."""
    form = BusquedaProductoForm(request.GET or None)
    productos = Producto.objects.select_related('categoria').all()

    if form.is_valid():
        q = form.cleaned_data.get('q')
        categoria = form.cleaned_data.get('categoria')
        estado = form.cleaned_data.get('estado')

        if q:
            productos = productos.filter(
                Q(nombre__icontains=q) | Q(descripcion__icontains=q)
            )
        if categoria:
            productos = productos.filter(categoria=categoria)
        if estado:
            productos = productos.filter(estado=estado)

    context = {
        'productos': productos,
        'form': form,
        'total': productos.count(),
    }
    return render(request, 'productos/producto_lista.html', context)


def producto_detalle(request, pk):
    """Detalle de un producto."""
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'productos/producto_detalle.html', {'producto': producto})


def producto_crear(request):
    """Crear un nuevo producto."""
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.nombre}" creado correctamente.')
            return redirect('producto_lista')
    else:
        form = ProductoForm()

    return render(request, 'productos/producto_form.html', {
        'form': form,
        'titulo': 'Nuevo Producto',
        'accion': 'Crear',
    })


def producto_editar(request, pk):
    """Editar un producto existente."""
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Producto "{producto.nombre}" actualizado correctamente.')
            return redirect('producto_lista')
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'productos/producto_form.html', {
        'form': form,
        'producto': producto,
        'titulo': f'Editar: {producto.nombre}',
        'accion': 'Guardar cambios',
    })


def producto_eliminar(request, pk):
    """Eliminar un producto (con confirmación)."""
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'Producto "{nombre}" eliminado correctamente.')
        return redirect('producto_lista')

    return render(request, 'productos/producto_confirmar_eliminar.html', {'producto': producto})


# ─────────────────────────────────────────────
#  CATEGORÍAS — CRUD
# ─────────────────────────────────────────────

def categoria_lista(request):
    """Lista de categorías con conteo de productos."""
    categorias = Categoria.objects.annotate(
        total_productos=Count('productos')
    ).order_by('nombre')
    return render(request, 'productos/categoria_lista.html', {'categorias': categorias})


def categoria_crear(request):
    """Crear una nueva categoría."""
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" creada correctamente.')
            return redirect('categoria_lista')
    else:
        form = CategoriaForm()

    return render(request, 'productos/categoria_form.html', {
        'form': form,
        'titulo': 'Nueva Categoría',
        'accion': 'Crear',
    })


def categoria_editar(request, pk):
    """Editar una categoría existente."""
    categoria = get_object_or_404(Categoria, pk=pk)

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" actualizada correctamente.')
            return redirect('categoria_lista')
    else:
        form = CategoriaForm(instance=categoria)

    return render(request, 'productos/categoria_form.html', {
        'form': form,
        'categoria': categoria,
        'titulo': f'Editar: {categoria.nombre}',
        'accion': 'Guardar cambios',
    })


def categoria_eliminar(request, pk):
    """Eliminar una categoría (con confirmación)."""
    categoria = get_object_or_404(Categoria, pk=pk)

    if request.method == 'POST':
        nombre = categoria.nombre
        categoria.delete()
        messages.success(request, f'Categoría "{nombre}" eliminada correctamente.')
        return redirect('categoria_lista')

    return render(request, 'productos/categoria_confirmar_eliminar.html', {'categoria': categoria})
