
-- Public rooms table for lobby browser
CREATE TABLE public.public_rooms (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  room_code text NOT NULL UNIQUE,
  host_name text NOT NULL DEFAULT 'Piloto',
  host_ship text NOT NULL DEFAULT 'phantom',
  map_id text NOT NULL DEFAULT 'neon-grid',
  player_count integer NOT NULL DEFAULT 1,
  max_players integer NOT NULL DEFAULT 6,
  status text NOT NULL DEFAULT 'waiting',
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_at timestamp with time zone NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.public_rooms ENABLE ROW LEVEL SECURITY;

-- Anyone can read public rooms
CREATE POLICY "Anyone can read public rooms" ON public.public_rooms
  FOR SELECT TO anon, authenticated USING (true);

-- Anyone can insert rooms (no auth required for quick play)
CREATE POLICY "Anyone can insert rooms" ON public.public_rooms
  FOR INSERT TO anon, authenticated WITH CHECK (true);

-- Anyone can update rooms (for player count updates)
CREATE POLICY "Anyone can update rooms" ON public.public_rooms
  FOR UPDATE TO anon, authenticated USING (true);

-- Anyone can delete rooms (for cleanup)
CREATE POLICY "Anyone can delete rooms" ON public.public_rooms
  FOR DELETE TO anon, authenticated USING (true);

-- Enable realtime for public_rooms
ALTER PUBLICATION supabase_realtime ADD TABLE public.public_rooms;
