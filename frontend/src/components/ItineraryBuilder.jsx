import React, { useState } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';

const ItineraryBuilder = ({ places, placesGeo }) => {
  const [itinerary, setItinerary] = useState([]);
  const [availablePlaces, setAvailablePlaces] = useState(
    placesGeo?.map((p, idx) => ({ id: `place-${idx}`, name: p.name || places?.[idx], ...p })) || []
  );

  const onDragEnd = (result) => {
    const { source, destination } = result;

    if (!destination) return;

    if (source.droppableId === destination.droppableId) {
      // Reordering within same list
      const items = source.droppableId === 'available' ? [...availablePlaces] : [...itinerary];
      const [reorderedItem] = items.splice(source.index, 1);
      items.splice(destination.index, 0, reorderedItem);
      
      if (source.droppableId === 'available') {
        setAvailablePlaces(items);
      } else {
        setItinerary(items);
      }
    } else {
      // Moving between lists
      const sourceClone = source.droppableId === 'available' ? [...availablePlaces] : [...itinerary];
      const destClone = destination.droppableId === 'available' ? [...availablePlaces] : [...itinerary];
      const [removed] = sourceClone.splice(source.index, 1);
      destClone.splice(destination.index, 0, removed);

      if (source.droppableId === 'available') {
        setAvailablePlaces(sourceClone);
        setItinerary(destClone);
      } else {
        setItinerary(sourceClone);
        setAvailablePlaces(destClone);
      }
    }
  };

  const clearItinerary = () => {
    setAvailablePlaces([...availablePlaces, ...itinerary].sort((a, b) => 
      a.name?.localeCompare(b.name)
    ));
    setItinerary([]);
  };

  const downloadItinerary = () => {
    if (itinerary.length === 0) {
      alert('Add some places to your itinerary first!');
      return;
    }

    const text = itinerary.map((place, idx) => 
      `${idx + 1}. ${place.name}`
    ).join('\n');

    const blob = new Blob([`My Travel Itinerary\n\n${text}`], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'itinerary.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!places || places.length === 0) return null;

  return (
    <div className="itinerary-builder">
      <div className="itinerary-header">
        <h3>🗺️ Build Your Itinerary</h3>
        <div className="itinerary-actions">
          <button onClick={clearItinerary} className="itinerary-btn clear-btn" title="Clear itinerary">
            🗑️ Clear
          </button>
          <button onClick={downloadItinerary} className="itinerary-btn download-btn" title="Download as text">
            📥 Download
          </button>
        </div>
      </div>
      
      <DragDropContext onDragEnd={onDragEnd}>
        <div className="itinerary-columns">
          <div className="itinerary-column">
            <h4>Available Places</h4>
            <Droppable droppableId="available">
              {(provided, snapshot) => (
                <div
                  {...provided.droppableProps}
                  ref={provided.innerRef}
                  className={`itinerary-list ${snapshot.isDraggingOver ? 'dragging-over' : ''}`}
                >
                  {availablePlaces.length === 0 ? (
                    <p className="empty-message">All places added to itinerary! 🎉</p>
                  ) : (
                    availablePlaces.map((place, index) => (
                      <Draggable key={place.id} draggableId={place.id} index={index}>
                        {(provided, snapshot) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            className={`itinerary-item ${snapshot.isDragging ? 'dragging' : ''}`}
                          >
                            <span className="drag-handle">⋮⋮</span>
                            <span className="place-name">{place.name}</span>
                          </div>
                        )}
                      </Draggable>
                    ))
                  )}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </div>

          <div className="itinerary-column">
            <h4>My Itinerary ({itinerary.length})</h4>
            <Droppable droppableId="itinerary">
              {(provided, snapshot) => (
                <div
                  {...provided.droppableProps}
                  ref={provided.innerRef}
                  className={`itinerary-list ${snapshot.isDraggingOver ? 'dragging-over' : ''}`}
                >
                  {itinerary.length === 0 ? (
                    <p className="empty-message">Drag places here to build your itinerary</p>
                  ) : (
                    itinerary.map((place, index) => (
                      <Draggable key={place.id} draggableId={place.id} index={index}>
                        {(provided, snapshot) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            className={`itinerary-item ${snapshot.isDragging ? 'dragging' : ''}`}
                          >
                            <span className="item-number">{index + 1}.</span>
                            <span className="drag-handle">⋮⋮</span>
                            <span className="place-name">{place.name}</span>
                          </div>
                        )}
                      </Draggable>
                    ))
                  )}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </div>
        </div>
      </DragDropContext>
      
      <p className="itinerary-hint">💡 Drag and drop places to create your custom itinerary</p>
    </div>
  );
};

export default ItineraryBuilder;
