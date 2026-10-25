insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('camera-captures', 'camera-captures', true, 5242880, array['image/jpeg'])
on conflict (id) do update
set public = excluded.public,
    file_size_limit = excluded.file_size_limit,
    allowed_mime_types = excluded.allowed_mime_types;

drop policy if exists "Public can read camera captures" on storage.objects;
create policy "Public can read camera captures"
on storage.objects
for select
to anon, authenticated
using (bucket_id = 'camera-captures');

create schema if not exists private;

create table if not exists private.camera_capture_rate_limits (
    ip_hash text not null,
    window_start timestamptz not null,
    request_count integer not null default 0,
    primary key (ip_hash, window_start)
);

create or replace function public.consume_camera_capture_rate_limit(
    p_ip_hash text,
    p_window_start timestamptz,
    p_limit integer
)
returns boolean
language plpgsql
security definer
set search_path = ''
as $$
declare
    current_count integer;
begin
    delete from private.camera_capture_rate_limits
    where window_start < now() - interval '24 hours';

    insert into private.camera_capture_rate_limits (ip_hash, window_start, request_count)
    values (p_ip_hash, p_window_start, 1)
    on conflict (ip_hash, window_start)
    do update set request_count = private.camera_capture_rate_limits.request_count + 1
    returning request_count into current_count;

    return current_count <= p_limit;
end;
$$;

revoke all on function public.consume_camera_capture_rate_limit(text, timestamptz, integer) from public, anon, authenticated;
grant execute on function public.consume_camera_capture_rate_limit(text, timestamptz, integer) to service_role;
