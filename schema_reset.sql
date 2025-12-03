-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- DROP EVERYTHING to ensure a clean slate
-- Order matters due to foreign keys
drop table if exists public.messages;
drop table if exists public.tasks;
drop table if exists public.applications;
drop table if exists public.internships;
drop table if exists public.profiles_names;
drop table if exists public.profiles; -- Drop the old table if it exists

-- 1. Profiles Table (Extends Supabase Auth)
create table public.profiles_names (
  id uuid references auth.users not null primary key,
  email text,
  role text check (role in ('student', 'company')),
  full_name text,
  -- Student specific fields
  resume_url text,
  portfolio_url text,
  skills text[],
  -- Company specific fields
  company_name text,
  company_description text,
  website text,
  
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable RLS
alter table public.profiles_names enable row level security;

-- Policies for Profiles
create policy "Public profiles are viewable by everyone."
  on profiles_names for select
  using ( true );

create policy "Users can insert their own profile."
  on profiles_names for insert
  with check ( auth.uid() = id );

create policy "Users can update own profile."
  on profiles_names for update
  using ( auth.uid() = id );

-- 2. Internships Table
create table public.internships (
  id uuid default uuid_generate_v4() primary key,
  company_id uuid references public.profiles_names(id) not null,
  title text not null,
  description text not null,
  role text not null,
  duration text,
  stipend text,
  location text,
  skills_required text[],
  status text default 'open' check (status in ('open', 'closed')),
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.internships enable row level security;

create policy "Internships are viewable by everyone."
  on internships for select
  using ( true );

create policy "Companies can insert internships."
  on internships for insert
  with check ( auth.uid() = company_id );

create policy "Companies can update their internships."
  on internships for update
  using ( auth.uid() = company_id );

-- 3. Applications Table
create table public.applications (
  id uuid default uuid_generate_v4() primary key,
  internship_id uuid references public.internships(id) not null,
  student_id uuid references public.profiles_names(id) not null,
  cover_letter text,
  resume_link text,
  status text default 'pending' check (status in ('pending', 'accepted', 'rejected')),
  applied_at timestamp with time zone default timezone('utc'::text, now()) not null,
  unique(internship_id, student_id)
);

alter table public.applications enable row level security;

create policy "Students can see their own applications."
  on applications for select
  using ( auth.uid() = student_id );

create policy "Companies can see applications for their internships."
  on applications for select
  using ( 
    exists (
      select 1 from internships 
      where internships.id = applications.internship_id 
      and internships.company_id = auth.uid()
    )
  );

create policy "Students can insert applications."
  on applications for insert
  with check ( auth.uid() = student_id );

create policy "Companies can update application status."
  on applications for update
  using ( 
    exists (
      select 1 from internships 
      where internships.id = applications.internship_id 
      and internships.company_id = auth.uid()
    )
  );

-- 4. Tasks Table
create table public.tasks (
  id uuid default uuid_generate_v4() primary key,
  internship_id uuid references public.internships(id) not null,
  student_id uuid references public.profiles_names(id) not null,
  title text not null,
  description text,
  due_date date,
  status text default 'pending' check (status in ('pending', 'submitted', 'completed')),
  submission_link text,
  feedback text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.tasks enable row level security;

create policy "Users can view tasks related to them"
  on tasks for select
  using ( 
    auth.uid() = student_id OR 
    exists (
      select 1 from internships 
      where internships.id = tasks.internship_id 
      and internships.company_id = auth.uid()
    )
  );

create policy "Companies can insert tasks"
  on tasks for insert
  with check (
    exists (
      select 1 from internships 
      where internships.id = tasks.internship_id 
      and internships.company_id = auth.uid()
    )
  );

create policy "Users can update tasks (Students submit, Companies review)"
  on tasks for update
  using (
    auth.uid() = student_id OR 
    exists (
      select 1 from internships 
      where internships.id = tasks.internship_id 
      and internships.company_id = auth.uid()
    )
  );

-- 5. Messages Table (Simple implementation)
create table public.messages (
  id uuid default uuid_generate_v4() primary key,
  sender_id uuid references public.profiles_names(id) not null,
  receiver_id uuid references public.profiles_names(id) not null,
  content text not null,
  read boolean default false,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.messages enable row level security;

create policy "Users can view their own messages"
  on messages for select
  using ( auth.uid() = sender_id or auth.uid() = receiver_id );

create policy "Users can send messages"
  on messages for insert
  with check ( auth.uid() = sender_id );

-- Trigger to handle new user creation
create or replace function public.handle_new_user() 
returns trigger as $$
begin
  insert into public.profiles_names (id, email, role, full_name)
  values (new.id, new.email, new.raw_user_meta_data->>'role', new.raw_user_meta_data->>'full_name');
  return new;
end;
$$ language plpgsql security definer;

-- Drop trigger if exists to avoid duplication error
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
