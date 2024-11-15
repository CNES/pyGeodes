pygeodes.utils.stac.Collection
==============================

.. currentmodule:: pygeodes.utils.stac

.. autoclass:: Collection
   :members:                                    <-- add at least this line
   :show-inheritance:                           <-- plus I want to show inheritance...
   :inherited-members:                          <-- ...and inherited members too

   
   .. automethod:: __init__

   
   .. rubric:: Methods

   .. autosummary::
   
      ~Collection.__init__
      ~Collection.add_asset
      ~Collection.add_child
      ~Collection.add_children
      ~Collection.add_item
      ~Collection.add_items
      ~Collection.add_link
      ~Collection.add_links
      ~Collection.clear_children
      ~Collection.clear_items
      ~Collection.clear_links
      ~Collection.clone
      ~Collection.delete_asset
      ~Collection.describe
      ~Collection.find
      ~Collection.from_dict
      ~Collection.from_file
      ~Collection.from_stac_collection
      ~Collection.full_copy
      ~Collection.fully_resolve
      ~Collection.generate_subcatalogs
      ~Collection.get_all_collections
      ~Collection.get_all_items
      ~Collection.get_assets
      ~Collection.get_child
      ~Collection.get_child_links
      ~Collection.get_children
      ~Collection.get_collections
      ~Collection.get_item
      ~Collection.get_item_links
      ~Collection.get_items
      ~Collection.get_links
      ~Collection.get_parent
      ~Collection.get_root
      ~Collection.get_root_link
      ~Collection.get_self_href
      ~Collection.get_single_link
      ~Collection.get_stac_objects
      ~Collection.is_relative
      ~Collection.list_available_keys
      ~Collection.make_all_asset_hrefs_absolute
      ~Collection.make_all_asset_hrefs_relative
      ~Collection.make_asset_hrefs_absolute
      ~Collection.make_asset_hrefs_relative
      ~Collection.map_assets
      ~Collection.map_items
      ~Collection.matches_object_type
      ~Collection.normalize_and_save
      ~Collection.normalize_hrefs
      ~Collection.remove_child
      ~Collection.remove_hierarchical_links
      ~Collection.remove_item
      ~Collection.remove_links
      ~Collection.resolve_links
      ~Collection.save
      ~Collection.save_object
      ~Collection.set_parent
      ~Collection.set_root
      ~Collection.set_self_href
      ~Collection.target_in_hierarchy
      ~Collection.to_dict
      ~Collection.update_extent_from_items
      ~Collection.validate
      ~Collection.validate_all
      ~Collection.walk
   
   

   
   
   .. rubric:: Attributes

   .. autosummary::
   
      ~Collection.DEFAULT_FILE_NAME
      ~Collection.STAC_OBJECT_TYPE
      ~Collection.self_href
      ~Collection.assets
      ~Collection.description
      ~Collection.extent
      ~Collection.id
      ~Collection.stac_extensions
      ~Collection.title
      ~Collection.keywords
      ~Collection.providers
      ~Collection.summaries
      ~Collection.links
      ~Collection.extra_fields
      ~Collection.catalog_type
   
   