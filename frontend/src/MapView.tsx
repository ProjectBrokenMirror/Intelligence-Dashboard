import { useMemo } from "react";
import { CircleMarker, MapContainer, Popup, TileLayer } from "react-leaflet";
import type { Item } from "./api";
import "leaflet/dist/leaflet.css";

const PV_CENTER: [number, number] = [20.6534, -105.2253];
const BOUNDS: [[number, number], [number, number]] = [
  [20.45, -105.52],
  [21.02, -105.05],
];

function categoryColor(cat: string): string {
  switch (cat) {
    case "safety":
      return "#c94c4c";
    case "infrastructure":
      return "#c9a227";
    case "event":
      return "#5b7fd1";
    default:
      return "#3db8a6";
  }
}

type Props = {
  items: Item[];
  selectedId: number | null;
  onSelect: (id: number) => void;
};

export default function MapView({ items, selectedId, onSelect }: Props) {
  const placed = useMemo(
    () => items.filter((i) => i.lat != null && i.lng != null) as (Item & { lat: number; lng: number })[],
    [items]
  );

  return (
    <div className="map-wrap">
      <MapContainer
        center={PV_CENTER}
        zoom={11}
        minZoom={9}
        maxZoom={16}
        maxBounds={BOUNDS}
        maxBoundsViscosity={0.85}
        scrollWheelZoom
        style={{ height: "440px", width: "100%", borderRadius: "10px" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {placed.map((it) => (
          <CircleMarker
            key={it.id}
            center={[it.lat, it.lng]}
            radius={selectedId === it.id ? 13 : 9}
            pathOptions={{
              color: categoryColor(it.category),
              fillColor: categoryColor(it.category),
              fillOpacity: 0.88,
              weight: 2,
            }}
            eventHandlers={{
              click: () => onSelect(it.id),
            }}
          >
            <Popup>
              <a href={it.url} target="_blank" rel="noreferrer noopener">
                {it.title}
              </a>
              <div className="muted small" style={{ marginTop: "0.35rem" }}>
                {it.category} · {it.severity}
                {it.neighborhood ? ` · ${it.neighborhood}` : ""}
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
      {placed.length === 0 && (
        <p className="muted map-hint">
          No geocoded items yet. Headlines that mention a known neighborhood (see server config) appear
          here after ingest.
        </p>
      )}
    </div>
  );
}
