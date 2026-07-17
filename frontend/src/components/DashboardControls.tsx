import type { ResourceSort } from "../lib/resources";

type Props = {
  query: string;
  tag: string;
  sort: ResourceSort;
  tags: string[];
  onQueryChange: (value: string) => void;
  onTagChange: (value: string) => void;
  onSortChange: (value: ResourceSort) => void;
};

export function DashboardControls({
  query,
  tag,
  sort,
  tags,
  onQueryChange,
  onTagChange,
  onSortChange,
}: Props) {
  return (
    <div className="controls" aria-label="Resource filters">
      <label className="control-field search-field">
        <span>Search</span>
        <input
          className="search"
          placeholder="Resources, tags, descriptions…"
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
        />
      </label>
      <label className="control-field">
        <span>Tag</span>
        <select className="select" value={tag} onChange={(event) => onTagChange(event.target.value)}>
          {tags.map((item) => (
            <option key={item} value={item}>{item === "all" ? "All tags" : item}</option>
          ))}
        </select>
      </label>
      <label className="control-field">
        <span>Sort</span>
        <select
          className="select"
          value={sort}
          onChange={(event) => onSortChange(event.target.value as ResourceSort)}
        >
          <option value="recent">Most recent</option>
          <option value="name">Name</option>
        </select>
      </label>
    </div>
  );
}
