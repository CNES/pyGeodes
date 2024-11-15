pygeodes.utils.stac.Item
========================

.. currentmodule:: pygeodes.utils.stac

.. autoclass:: Item
   :members:                                    <-- add at least this line
   :show-inheritance:                           <-- plus I want to show inheritance...
   :inherited-members:                          <-- ...and inherited members too

   
   .. automethod:: __init__

   
   .. rubric:: Methods

   .. autosummary::
   
      ~Item.__init__
      ~Item.add_asset
      ~Item.add_derived_from
      ~Item.add_link
      ~Item.add_links
      ~Item.clear_links
      ~Item.clone
      ~Item.delete_asset
      ~Item.download_archive
      ~Item.find
      ~Item.from_dict
      ~Item.from_file
      ~Item.full_copy
      ~Item.get_assets
      ~Item.get_collection
      ~Item.get_datetime
      ~Item.get_derived_from
      ~Item.get_links
      ~Item.get_parent
      ~Item.get_quicklook_content_in_base64
      ~Item.get_root
      ~Item.get_root_link
      ~Item.get_self_href
      ~Item.get_single_link
      ~Item.get_stac_objects
      ~Item.list_available_keys
      ~Item.make_asset_hrefs_absolute
      ~Item.make_asset_hrefs_relative
      ~Item.matches_object_type
      ~Item.remove_derived_from
      ~Item.remove_hierarchical_links
      ~Item.remove_links
      ~Item.resolve_links
      ~Item.save_object
      ~Item.set_collection
      ~Item.set_datetime
      ~Item.set_parent
      ~Item.set_root
      ~Item.set_self_href
      ~Item.show_quicklook
      ~Item.target_in_hierarchy
      ~Item.to_dict
      ~Item.validate
   
   

   
   
   .. rubric:: Attributes

   .. autosummary::
   
      ~Item.STAC_OBJECT_TYPE
      ~Item.common_metadata
      ~Item.data_asset
      ~Item.data_asset_checksum
      ~Item.filesize
      ~Item.quicklook_asset
      ~Item.s3_path
      ~Item.self_href
      ~Item.assets
      ~Item.bbox
      ~Item.collection
      ~Item.collection_id
      ~Item.datetime
      ~Item.extra_fields
      ~Item.geometry
      ~Item.id
      ~Item.links
      ~Item.properties
      ~Item.stac_extensions
   
   