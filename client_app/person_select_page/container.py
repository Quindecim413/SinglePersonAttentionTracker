from dependency_injector import providers, containers

from client_app.person_select_page.view import SelectPersonPage
from client_app.widgets.person_select import PersonSelectionWidget
from common.collections.persons import SelectedPersonCollection, AvailablePersonsCollection
from common.services.active_person import ActivePersonSelector
from common.services.active_work_state import ActiveWorkState
from common.widgets.preview_person import PersonPreviewWidget

class PersonSelectPageContainer(containers.DeclarativeContainer):
    scene = providers.DependenciesContainer()
    
    active_person_selector = providers.Dependency(instance_of=ActivePersonSelector)
    person_widget = providers.Factory(PersonPreviewWidget)
    available_persons_collection = providers.Factory(AvailablePersonsCollection,
                                                     active_person_selector=active_person_selector,
                                                     scene_initializer=scene.initializer)

    active_person_collection = providers.Factory(SelectedPersonCollection,
                                                 active_person_selector=active_person_selector)

    select_person_widget = providers.Factory(PersonSelectionWidget,
                                             persons_collection=available_persons_collection,
                                             active_person_collection=active_person_collection,
                                             short_person_widget_factory=person_widget.provider,
                                             expanded_person_widget_factory=person_widget.provider)
    
    page = providers.Factory(SelectPersonPage,
                             select_person_widget=select_person_widget)