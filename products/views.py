import json

from django.http import JsonResponse, Http404
from django.shortcuts import (
    render, HttpResponse, HttpResponseRedirect, reverse, get_object_or_404
)
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView

from core.views import LoginRequire
from products.models import Product, Category
from products.services import ProductManagement
from products.forms import ProductForm, CategoryForm
from stores.exceptions import UserNotInStoreException
from stores.services import StoreManagement


class ProductListView(LoginRequire, View):
    service_class = ProductManagement

    def get(self, request, store_name):
        try:
            StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        table_columns = ['', 'Mã sản phẩm', 'Tên sản phẩm', 'Giá bán', 'Giá vốn', 'Tồn kho']
        categories = Category.objects.all()
        context = {
            'table_columns': table_columns,
            'list_categories': categories,
            'active': 'products',
            'store_name': store_name
        }
        return render(request, template_name='product/products.html', context=context)

    def post(self, request, store_name):
        """
        Handle operations sorting, paging, getting of datatables.
        Return json response to datatables
        """
        try:
            store = StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()
        response = self.service_class(request, store).get_products_datatables()
        return JsonResponse(response)


class ProductCreationView(LoginRequire, View):
    model = Product
    form_class = ProductForm
    template_name = 'product/add_products.html'

    def get(self, request, store_name):
        try:
            StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        form = self.form_class()
        context = {
            'form': form,
            'action': 'add',
            'url': reverse('products:product-creation', args=[store_name]),
            'active': 'products',
            'store_name': store_name
        }
        return render(request, self.template_name, context=context)

    def post(self, request, store_name):
        try:
            store = StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save(store=store)
            return self.get(request, store_name)

        context = {
            'form': form,
            'url': reverse('products:product-creation', args=[store_name]),
            'store_name': store_name
        }
        return render(request, self.template_name, context=context)


class ProductDetailView(LoginRequire, View):
    model = Product
    template_name = 'product/detail_product.html'
    context_object_name = 'product'
    queryset = Product.objects.all()

    def get(self, request, store_name, pk):
        try:
            StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        product = get_object_or_404(self.model, pk=pk)
        list_imgs = product.get_list_images()
        if not list_imgs:
            list_imgs.append('/resource/images/default_product.jpg')

        context = {
            self.context_object_name: product,
            'list_imgs': list_imgs,
            'store_name': store_name
        }
        html = render(request, self.template_name, context=context)
        return HttpResponse(html)


class ProductUpdateView(LoginRequire, View):
    model = Product
    template_name = 'product/update_product.html'
    form_class = ProductForm
    queryset = Product.objects.all()
    lookup_field = 'pk'

    def get(self, request, store_name, pk):
        """
        Return a product form as html.
        Change product's available property to INT type if product's unit property equal UNIT_INT
        """
        try:
            StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        product = get_object_or_404(self.model, pk=pk)
        if product.unit == Product.UNIT_INT:
            # change available to INT type
            product.available = int(product.available)

        form = self.form_class(instance=product)
        context = {
            'action': 'update',
            'form': form,
            'url': reverse('products:product-update', args=[store_name, pk]),
        }
        html = render(request, self.template_name, context=context)
        return HttpResponse(html)

    def post(self, request, store_name, pk):
        try:
            StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

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

    def patch(self, request, store_name, *args, **kwargs):
        """
        Change status of product or list products.
        """
        try:
            StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        if self.lookup_field in kwargs:
            _id = kwargs[self.lookup_field]
            product = get_object_or_404(self.model, pk=_id)
            product.status = 2
            product.save()
        else:
            ids = request.PATCH.getlist('list_ids[]')
            new_status = int(request.PATCH.get("newStatus"))
            objs = self.model.objects.filter(id__in=ids)
            if objs and len(objs) > 0:
                for obj in objs:
                    obj.status = new_status
                self.model.objects.bulk_update(objs, ['status'])

        return JsonResponse({'status': 'success'})

    def delete(self, request, store_name, *args, **kwargs):
        """
        Move a product or list products to trash (status = 0)
        """
        try:
            StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

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


class ProductDeleteView(LoginRequire, DeleteView):
    model = Product
    queryset = Product.objects.all()

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


class CategoryCreationView(LoginRequire, View):
    model = Category
    form_class = CategoryForm
    template_name = "category/add_category.html"

    def get(self, request, store_name):
        try:
            StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        form = self.form_class()
        context = {
            "form": form,
            "store_name": store_name
        }
        return render(request, template_name=self.template_name, context=context)

    def post(self, request, store_name):
        try:
            store = StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        form = self.form_class(request.POST)
        if form.is_valid():
            form.save(store=store)
            response = {
                "status": "success"
            }
            return JsonResponse(data=response, status=200)
        errors = []
        for field in form:
            for error in field.errors:
                errors.append({'id': field.auto_id, 'error': error})
        response = {
            "status": "failed",
            "data": errors
        }
        return JsonResponse(data=response, status=200)


class CategoryDetailUpdateView(LoginRequire, View):
    model = Category
    form_class = CategoryForm

    def get(self, request, store_name, pk):
        try:
            StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        category = get_object_or_404(self.model, pk=pk)
        form = self.form_class(instance=category)
        context = {
            "form": form,
            "id": category.id,
            "store_name": store_name
        }
        return render(request, template_name="category/update_category.html", context=context)

    def post(self, request, store_name, pk):
        try:
            StoreManagement.valid_store_user(store_name, request.user)
        except UserNotInStoreException:
            raise Http404()

        category = get_object_or_404(self.model, pk=pk)
        form = self.form_class(request.POST, instance=category)
        response = {'status': 'success'}
        if form.is_valid():
            form.save()
        else:
            response['status'] = "failed"
            errors = []
            for field in form:
                for error in field.errors:
                    errors.append({'id': field.auto_id, 'error': error})
            response['data'] = errors
        return JsonResponse(data=response, status=200)
