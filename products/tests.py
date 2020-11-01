from django.test import TestCase
from products.services import ProductServices, ProductAlreadyExistsError, CategoryNotExistsError
from products.models import Product, Category


class ProductServicesTestCase(TestCase):
    def test_product_code_exists(self):
        c = Category.objects.create(category_name='NN')
        p = Product.objects.create(product_code='SP1',
                                   product_name='Bim',
                                   barcode='123',
                                   sell_price=156,
                                   category_id=c.id
                                   )
        expect_result = "Mã sản phẩm 'SP1' đã tồn tại"
        error_msg = ''
        try:
            ps = ProductServices(product_name='Bim2',
                                 product_code='SP1',
                                 sell_price=213,
                                 cost_price=123,
                                 available=123,
                                 category_name='NN'
                                 )
            ps.execute()
        except CategoryNotExistsError as e:
            error_msg = str(e)
        except ProductAlreadyExistsError as e:
            error_msg = str(e)

        self.assertEqual(expect_result, error_msg)

    def test_product_name_exists(self):
        c = Category.objects.create(category_name='NN2')
        p = Product.objects.create(product_code='SP1',
                                   product_name='Bim',
                                   barcode='123',
                                   sell_price=156,
                                   category_id=c.id
                                   )
        expect_result = "Tên sản phẩm 'Bim' đã tồn tại"
        error_msg = ''
        try:
            ps = ProductServices(product_name='Bim',
                                 product_code='SP2',
                                 sell_price=213,
                                 cost_price=123,
                                 available=123,
                                 category_name='NN2'
                                 )
            ps.execute()
        except CategoryNotExistsError as e:
            error_msg = str(e)
        except ProductAlreadyExistsError as e:
            error_msg = str(e)

        self.assertEqual(expect_result, error_msg)

    def test_category_not_exists(self):
        expect_result = "Nhóm hàng 'NN' không tồn tại"
        error_msg = ''
        try:
            ps = ProductServices(product_name='Bim',
                                 product_code='SP001',
                                 sell_price=213,
                                 cost_price=123,
                                 available=123,
                                 category_name='NN'
                                 )
            ps.execute()
        except CategoryNotExistsError as e:
            error_msg = str(e)
        except ProductAlreadyExistsError as e:
            error_msg = str(e)

        self.assertEqual(expect_result, error_msg)

    def test_add_new_product_success(self):
        Category.objects.create(category_name='NN', description='ABC')
        expect_result = ''
        error_msg = ''
        pid = None
        try:
            ps = ProductServices(product_name='Bim',
                                 product_code='SP001',
                                 sell_price=213,
                                 cost_price=123,
                                 available=123,
                                 category_name='NN'
                                 )
            p = ps.execute()
        except CategoryNotExistsError as e:
            error_msg = str(e)
        except ProductAlreadyExistsError as e:
            error_msg = str(e)

        self.assertEqual(expect_result, error_msg)
        self.assertNotEqual(p.id, pid)
        self.assertEqual(p.id, 1)
