# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'CurrencyTable'
        db.create_table('library_currencytable', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_currency', self.gf('django.db.models.fields.IntegerField')()),
            ('to_currency', self.gf('django.db.models.fields.IntegerField')()),
            ('rate', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=5)),
        ))
        db.send_create_signal('library', ['CurrencyTable'])

        # Deleting field 'Price.delivery_price'
        db.delete_column('library_price', 'delivery_price')

        # Deleting field 'Price.currency'
        db.delete_column('library_price', 'currency')

        # Deleting field 'Price.price'
        db.delete_column('library_price', 'price')

        # Adding field 'Price.native_currency'
        db.add_column('library_price', 'native_currency', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)

        # Adding field 'Price.native_price'
        db.add_column('library_price', 'native_price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True), keep_default=False)

        # Adding field 'Price.native_delivery'
        db.add_column('library_price', 'native_delivery', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True), keep_default=False)

        # Adding field 'Price._native_total'
        db.add_column('library_price', '_native_total', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True), keep_default=False)

        # Adding field 'Price._converted_currency'
        db.add_column('library_price', '_converted_currency', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)

        # Adding field 'Price._converted_price'
        db.add_column('library_price', '_converted_price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True), keep_default=False)

        # Adding field 'Price._converted_delivery'
        db.add_column('library_price', '_converted_delivery', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True), keep_default=False)

        # Adding field 'Price._converted_total'
        db.add_column('library_price', '_converted_total', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'CurrencyTable'
        db.delete_table('library_currencytable')

        # Adding field 'Price.delivery_price'
        db.add_column('library_price', 'delivery_price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True), keep_default=False)

        # We cannot add back in field 'Price.currency'
        raise RuntimeError(
            "Cannot reverse this migration. 'Price.currency' and its values cannot be restored.")

        # Adding field 'Price.price'
        db.add_column('library_price', 'price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True), keep_default=False)

        # Deleting field 'Price.native_currency'
        db.delete_column('library_price', 'native_currency')

        # Deleting field 'Price.native_price'
        db.delete_column('library_price', 'native_price')

        # Deleting field 'Price.native_delivery'
        db.delete_column('library_price', 'native_delivery')

        # Deleting field 'Price._native_total'
        db.delete_column('library_price', '_native_total')

        # Deleting field 'Price._converted_currency'
        db.delete_column('library_price', '_converted_currency')

        # Deleting field 'Price._converted_price'
        db.delete_column('library_price', '_converted_price')

        # Deleting field 'Price._converted_delivery'
        db.delete_column('library_price', '_converted_delivery')

        # Deleting field 'Price._converted_total'
        db.delete_column('library_price', '_converted_total')


    models = {
        'library.book': {
            'Meta': {'ordering': "['isbn']", 'object_name': 'Book'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isbn': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'library.currencytable': {
            'Meta': {'ordering': "['from_currency']", 'object_name': 'CurrencyTable'},
            'from_currency': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '5'}),
            'to_currency': ('django.db.models.fields.IntegerField', [], {})
        },
        'library.price': {
            'Meta': {'ordering': "['-date_added']", 'object_name': 'Price'},
            '_converted_currency': ('django.db.models.fields.IntegerField', [], {}),
            '_converted_delivery': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            '_converted_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            '_converted_total': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            '_native_total': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['library.Book']"}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'error': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'native_currency': ('django.db.models.fields.IntegerField', [], {}),
            'native_delivery': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'native_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['library.Shop']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'library.shop': {
            'Meta': {'ordering': "['-featured', 'name']", 'object_name': 'Shop'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'delivery': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['library']
