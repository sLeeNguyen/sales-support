import json

from django.http import JsonResponse
from django.shortcuts import (
    render, HttpResponse, HttpResponseRedirect, reverse, get_object_or_404
)
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView

from core.views import LoginRequire
from products.models import Product
from products.services import ProductServices
from products.forms import ProductForm


class ProductListView(LoginRequire, View):
    active = 'products'

    def get(self, request):
        table_columns = ['', 'Mã sản phẩm', 'Tên sản phẩm', 'Giá bán', 'Giá vốn', 'Tồn kho']
        context = {'table_columns': table_columns, 'active': self.active}
        return render(request, template_name='product/products.html', context=context)

    def post(self, request):
        """
        Handle operations sorting, paging, getting of datatables.
        Return json response to datatables
        """
        response = ProductServices.get_products_datatables(request.POST)

        return HttpResponse(json.dumps(response))


class ProductCreationView(LoginRequire, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/add_products.html'

    def get(self, request):
        form = self.form_class()
        context = {
            'form': form,
            'action': 'add',
            'form_method': 'post',
            'url': reverse('products:product-creation')
        }
        return render(request, self.template_name, context=context)

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return self.get(request)

        context = {
            'form': form,
            'active': self.active,
            'url': reverse('products:product-creation')
        }
        return render(request, self.template_name, context=context)


class ProductDetailView(LoginRequire, DetailView):
    model = Product
    template_name = 'product/detail_product.html'
    context_object_name = 'product'
    queryset = Product.objects.all()

    def get(self, request, pk):
        product = get_object_or_404(self.model, pk=pk)
        list_imgs = product.get_list_images()
        if not list_imgs:
            list_imgs.append('/resource/images/default_product.jpg')

        context = {
            self.context_object_name: product,
            'list_imgs': list_imgs
        }
        html = render(request, self.template_name, context=context)
        return HttpResponse(html)


class ProductUpdateView(LoginRequire, View):
    model = Product
    template_name = 'product/update_product.html'
    form_class = ProductForm
    queryset = Product.objects.all()
    lookup_field = 'pk'

    def get(self, request, pk):
        """
        Return a product form as html.
        Change product's available property to INT type if product's unit property equal UNIT_INT
        """
        product = get_object_or_404(self.model, pk=pk)
        if product.unit == Product.UNIT_INT:
            # change available to INT type
            product.available = int(product.available)

        form = self.form_class(instance=product)
        context = {
            'action': 'update',
            'form': form,
            'url': reverse('products:product-update') + pk + "/",
        }
        html = render(request, self.template_name, context=context)
        return HttpResponse(html)

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        form = self.form_class(request.POST, request.FILES, instance=product)

        response = {'status': 'success'}
        if form.is_valid():
            form.save()
        else:
            response['status'] = 'failed'
            errors = []
            for field in form:
                for error in field.errors:
                    errors.append({'id': field.auto_id, 'error': error})
            response['data'] = errors

        return JsonResponse(data=response)

    def patch(self, request, *args, **kwargs):
        """
        Change status of product or list products to no sell
        """
        if self.lookup_field in kwargs:
            _id = kwargs[self.lookup_field]
            product = get_object_or_404(self.model, pk=_id)
            product.status = 2
            product.save()
        else:
            ids = request.PATCH.getlist('list_ids[]')
            objs = self.model.objects.filter(id__in=ids)
            if objs and len(objs) > 0:
                for obj in objs:
                    obj.status = 2
                self.model.objects.bulk_update(objs, ['status'])

        return JsonResponse({'status': 'success'})

    def delete(self, request, *args, **kwargs):
        """
        Move a product or list products to trash (status = 0)
        """
        if self.lookup_field in kwargs:
            _id = kwargs[self.lookup_field]
            product = get_object_or_404(self.model, pk=_id)
            product.status = 0
            product.save()
        else:
            ids = request.DELETE.getlist('list_ids[]')
            delete_objs = self.queryset.filter(id__in=ids)
            if delete_objs and len(delete_objs) > 0:
                for obj in delete_objs:
                    obj.status = 0
                self.model.objects.bulk_update(delete_objs, ['status'])

        return JsonResponse({'status': 'success'})


class ProductDeleteView(DeleteView):
    model = Product
    queryset = Product.objects.all()
    lookup_field = 'pk'

    def delete(self, request, *args, **kwargs):
        """
        Delete permanent a product or list products
        """
        if self.lookup_field in kwargs:
            _id = kwargs[self.lookup_field]
            product = get_object_or_404(self.model, pk=_id)
            product.delete()
        else:
            ids = request.DELETE.getlist('list_ids[]')
            delete_objs = self.queryset.filter(id__in=ids)
            if delete_objs and len(delete_objs) > 0:
                delete_objs.delete()
        return JsonResponse({'status': 'success'})
