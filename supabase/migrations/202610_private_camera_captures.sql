update storage.buckets
set public = false
where id = 'camera-captures';

drop policy if exists "Public can read camera captures" on storage.objects;