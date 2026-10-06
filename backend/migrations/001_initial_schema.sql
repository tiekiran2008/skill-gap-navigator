-- ============================================================
-- Skill Gap Navigator - Phase 7: Supabase Auth + Persistent Storage
-- ============================================================

-- 1. PROFILES (extends Supabase auth.users)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT DEFAULT '',
    email TEXT DEFAULT '',
    avatar_url TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own profile"
    ON public.profiles FOR DELETE
    USING (auth.uid() = user_id);

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (user_id, email, full_name)
    VALUES (NEW.id, NEW.email, COALESCE(NEW.raw_user_meta_data->>'full_name', ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();


-- 2. RESUMES
-- ============================================================
CREATE TABLE IF NOT EXISTS public.resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    filename TEXT NOT NULL DEFAULT '',
    parsed_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE public.resumes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own resumes"
    ON public.resumes FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own resumes"
    ON public.resumes FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own resumes"
    ON public.resumes FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own resumes"
    ON public.resumes FOR DELETE
    USING (auth.uid() = user_id);


-- 3. USER_SKILLS
-- ============================================================
CREATE TABLE IF NOT EXISTS public.user_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    skill_name TEXT NOT NULL,
    confidence REAL DEFAULT 0.0,
    source TEXT DEFAULT 'resume',
    created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE public.user_skills ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own skills"
    ON public.user_skills FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own skills"
    ON public.user_skills FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own skills"
    ON public.user_skills FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own skills"
    ON public.user_skills FOR DELETE
    USING (auth.uid() = user_id);


-- 4. CAREER_TARGETS
-- ============================================================
CREATE TABLE IF NOT EXISTS public.career_targets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    target_role TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE public.career_targets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own career targets"
    ON public.career_targets FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own career targets"
    ON public.career_targets FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own career targets"
    ON public.career_targets FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own career targets"
    ON public.career_targets FOR DELETE
    USING (auth.uid() = user_id);


-- 5. COMPANY_ANALYSES
-- ============================================================
CREATE TABLE IF NOT EXISTS public.company_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    analysis_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE public.company_analyses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own company analyses"
    ON public.company_analyses FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own company analyses"
    ON public.company_analyses FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own company analyses"
    ON public.company_analyses FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own company analyses"
    ON public.company_analyses FOR DELETE
    USING (auth.uid() = user_id);


-- 6. CAREER_ANALYSES
-- ============================================================
CREATE TABLE IF NOT EXISTS public.career_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    recommendations JSONB DEFAULT '[]',
    target_role TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE public.career_analyses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own career analyses"
    ON public.career_analyses FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own career analyses"
    ON public.career_analyses FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own career analyses"
    ON public.career_analyses FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own career analyses"
    ON public.career_analyses FOR DELETE
    USING (auth.uid() = user_id);


-- 7. ROADMAPS
-- ============================================================
CREATE TABLE IF NOT EXISTS public.roadmaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    target_role TEXT NOT NULL DEFAULT '',
    roadmap_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE public.roadmaps ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own roadmaps"
    ON public.roadmaps FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own roadmaps"
    ON public.roadmaps FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own roadmaps"
    ON public.roadmaps FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own roadmaps"
    ON public.roadmaps FOR DELETE
    USING (auth.uid() = user_id);


-- 8. ROADMAP_PROGRESS
-- ============================================================
CREATE TABLE IF NOT EXISTS public.roadmap_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    roadmap_id UUID NOT NULL REFERENCES public.roadmaps(id) ON DELETE CASCADE,
    skill_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Not Started' CHECK (status IN ('Not Started', 'Learning', 'Completed')),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE public.roadmap_progress ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own roadmap progress"
    ON public.roadmap_progress FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own roadmap progress"
    ON public.roadmap_progress FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own roadmap progress"
    ON public.roadmap_progress FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own roadmap progress"
    ON public.roadmap_progress FOR DELETE
    USING (auth.uid() = user_id);

-- Unique constraint: one progress entry per user+roadmap+skill
CREATE UNIQUE INDEX IF NOT EXISTS idx_roadmap_progress_unique
    ON public.roadmap_progress (user_id, roadmap_id, skill_name);


-- 9. ASSISTANT_CHAT_HISTORY
-- ============================================================
CREATE TABLE IF NOT EXISTS public.assistant_chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL DEFAULT '',
    tools_used JSONB DEFAULT '[]',
    relevant_skills JSONB DEFAULT '[]',
    suggested_action TEXT DEFAULT '',
    source TEXT DEFAULT 'fallback',
    created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE public.assistant_chat_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own chat history"
    ON public.assistant_chat_history FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chat history"
    ON public.assistant_chat_history FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own chat history"
    ON public.assistant_chat_history FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own chat history"
    ON public.assistant_chat_history FOR DELETE
    USING (auth.uid() = user_id);

CREATE INDEX IF NOT EXISTS idx_chat_history_user
    ON public.assistant_chat_history (user_id, created_at DESC);
