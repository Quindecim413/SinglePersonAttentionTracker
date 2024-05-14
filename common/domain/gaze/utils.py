from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DRender import Qt3DRender


def remove_entity_with_children(entity):
    # Function to recursively remove an entity and its children
    if entity is not None:
        # Recursively remove all children first
        for child in entity.children():
            if isinstance(child, Qt3DCore.QEntity):
                remove_entity_with_children(child)

        # Now remove the entity from its parent
        if entity.parent() is not None:
            entity.parent().removeChild(entity)

        # Finally, delete the entity to free up memory
        entity.deleteLater()


def remove_entity_and_components(entity):
    # Function to recursively remove an entity, its children, and components
    if entity is not None:
        # Detach or delete components if necessary
        for component in entity.components():
            # If the component isn't shared and you want to delete it:
            component.setParent(None)  # Detach the component
            component.deleteLater()    # Schedule component for deletion

        # Recursively remove all children
        for child in entity.children():
            if isinstance(child, Qt3DCore.QEntity):
                remove_entity_and_components(child)

        # Now remove the entity from its parent
        if entity.parent() is not None:
            entity.parent().removeChild(entity)

        # Finally, delete the entity
        entity.deleteLater()

# # Usage
# # Assuming 'entity' is the QEntity instance you want to remove
# remove_entity_and_components(entity)


def unpack_frame_graph(node:Qt3DRender.QFrameGraphNode):
    return {node:{child: unpack_frame_graph(child) for child in node.children() if isinstance(child, Qt3DRender.QFrameGraphNode)}}


   


