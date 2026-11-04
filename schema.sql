-- ==============================================================================
-- PERSONAL PORTFOLIO SUPABASE SCHEMA & ROW LEVEL SECURITY (RLS)
-- ==============================================================================

-- 1. EXTENSIONS
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. DROP TABLES IF RE-INITIALIZING (CAUTION: CASCADE)
DROP TABLE IF EXISTS project_images CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS skills CASCADE;
DROP TABLE IF EXISTS certifications CASCADE;
DROP TABLE IF EXISTS cv CASCADE;
DROP TABLE IF EXISTS profile CASCADE;

-- 3. TABLES DEFINITION

-- Profile Table (Single record holding owner info)
CREATE TABLE profile (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    tagline TEXT NOT NULL,
    bio TEXT NOT NULL,
    avatar_url TEXT,
    email TEXT,
    location TEXT DEFAULT 'San Francisco, CA',
    github_url TEXT,
    linkedin_url TEXT,
    twitter_url TEXT,
    website_url TEXT,
    available_for_hire BOOLEAN DEFAULT true,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Skills Table (Categorized tech competencies)
CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    category TEXT NOT NULL, -- 'Frontend', 'Backend & APIs', 'Cloud & DevOps', 'AI & Data Science'
    level INTEGER NOT NULL CHECK (level >= 1 AND level <= 100),
    icon TEXT, -- e.g. '🐍', '⚛️', '☁️'
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Projects Table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    tagline TEXT,
    description TEXT NOT NULL,
    tech_stack TEXT NOT NULL, -- Comma-separated (e.g. 'Python, FastAPI, Streamlit, Supabase')
    cover_image_url TEXT,
    live_url TEXT,
    github_url TEXT,
    featured BOOLEAN DEFAULT false,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Project Images (Multi-image gallery per project)
CREATE TABLE project_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    caption TEXT,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Certifications Table
CREATE TABLE certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    issuer TEXT NOT NULL,
    issue_date TEXT NOT NULL, -- e.g. 'Oct 2025' or '2025-10-01'
    credential_url TEXT,
    media_url TEXT, -- Direct link to Certificate image or PDF
    media_type TEXT DEFAULT 'image', -- 'image' or 'pdf'
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- CV Document Table
CREATE TABLE cv (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_name TEXT NOT NULL,
    file_url TEXT NOT NULL,
    version_label TEXT DEFAULT 'Latest Resume',
    is_active BOOLEAN DEFAULT true,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. ROW LEVEL SECURITY (RLS) POLICIES

-- Enable RLS on all tables
ALTER TABLE profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_images ENABLE ROW LEVEL SECURITY;
ALTER TABLE certifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE cv ENABLE ROW LEVEL SECURITY;

-- PUBLIC READ POLICIES (Anonymous and Authenticated can read)
CREATE POLICY "Public read on profile" ON profile FOR SELECT USING (true);
CREATE POLICY "Public read on skills" ON skills FOR SELECT USING (true);
CREATE POLICY "Public read on projects" ON projects FOR SELECT USING (true);
CREATE POLICY "Public read on project_images" ON project_images FOR SELECT USING (true);
CREATE POLICY "Public read on certifications" ON certifications FOR SELECT USING (true);
CREATE POLICY "Public read on cv" ON cv FOR SELECT USING (true);

-- AUTHENTICATED ADMIN WRITE POLICIES (Only logged-in admin can insert/update/delete)
CREATE POLICY "Admin write on profile" ON profile FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "Admin write on skills" ON skills FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "Admin write on projects" ON projects FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "Admin write on project_images" ON project_images FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "Admin write on certifications" ON certifications FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "Admin write on cv" ON cv FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- 5. STORAGE BUCKETS CONFIGURATION
-- Buckets: 'images' (profile photo, project covers, screenshots, certs) and 'documents' (CV PDFs)
INSERT INTO storage.buckets (id, name, public)
VALUES 
    ('images', 'images', true),
    ('documents', 'documents', true)
ON CONFLICT (id) DO UPDATE SET public = true;

-- Storage policies: Public can read, only Authenticated can upload/modify
CREATE POLICY "Public Access Images" ON storage.objects FOR SELECT USING (bucket_id = 'images');
CREATE POLICY "Public Access Documents" ON storage.objects FOR SELECT USING (bucket_id = 'documents');

CREATE POLICY "Admin Upload Images" ON storage.objects FOR INSERT TO authenticated WITH CHECK (bucket_id = 'images');
CREATE POLICY "Admin Update Images" ON storage.objects FOR UPDATE TO authenticated USING (bucket_id = 'images');
CREATE POLICY "Admin Delete Images" ON storage.objects FOR DELETE TO authenticated USING (bucket_id = 'images');

CREATE POLICY "Admin Upload Documents" ON storage.objects FOR INSERT TO authenticated WITH CHECK (bucket_id = 'documents');
CREATE POLICY "Admin Update Documents" ON storage.objects FOR UPDATE TO authenticated USING (bucket_id = 'documents');
CREATE POLICY "Admin Delete Documents" ON storage.objects FOR DELETE TO authenticated USING (bucket_id = 'documents');

-- 6. REALISTIC STARTER SEED DATA (NO LOREM IPSUM)
INSERT INTO profile (name, tagline, bio, avatar_url, email, location, github_url, linkedin_url, website_url, available_for_hire)
VALUES (
    'Alex Rivers',
    'Senior Full-Stack Engineer & AI Systems Architect',
    'I build resilient distributed backend services, high-performance web applications, and production-grade LLM interfaces. Passionate about clean code, intuitive UI/UX design, and cloud scalability.',
    'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=600&q=80',
    'alex.rivers.dev@gmail.com',
    'San Francisco, CA / Remote',
    'https://github.com',
    'https://linkedin.com',
    'https://alexrivers.dev',
    true
);

INSERT INTO skills (name, category, level, icon, display_order)
VALUES
    ('Python & AsyncIO', 'Backend & APIs', 95, '🐍', 1),
    ('FastAPI & Django', 'Backend & APIs', 90, '⚡', 2),
    ('PostgreSQL & Supabase', 'Backend & APIs', 92, '🐘', 3),
    ('Redis & Celery', 'Backend & APIs', 85, '🔴', 4),
    ('React & Next.js', 'Frontend & UI', 88, '⚛️', 5),
    ('TypeScript & Tailwind CSS', 'Frontend & UI', 90, '🎨', 6),
    ('Streamlit & Dash', 'Frontend & UI', 94, '📊', 7),
    ('Docker & Kubernetes', 'Cloud & DevOps', 86, '🐳', 8),
    ('AWS & Terraform', 'Cloud & DevOps', 84, '☁️', 9),
    ('CI/CD & GitHub Actions', 'Cloud & DevOps', 90, '🚀', 10),
    ('LangChain & RAG Architectures', 'AI & Machine Learning', 88, '🤖', 11),
    ('PyTorch & Model Serving', 'AI & Machine Learning', 82, '🧠', 12);

INSERT INTO projects (title, tagline, description, tech_stack, cover_image_url, live_url, github_url, featured, display_order)
VALUES
    (
        'OmniQuery: Enterprise RAG Knowledge Assistant',
        'Multi-tenant semantic search engine indexing 50,000+ technical documents.',
        'Engineered an enterprise semantic search and question-answering assistant using hybrid dense/sparse retrieval. Features multi-tenant document isolation, automated citation generation, streaming responses, and sub-second query latency.',
        'Python, FastAPI, Supabase pgvector, LangChain, OpenAI, Docker',
        'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1000&q=80',
        'https://example.com/omniquery',
        'https://github.com/example/omniquery',
        true,
        1
    ),
    (
        'ApexTelemetry: Real-Time Fleet Telemetry Platform',
        'High-throughput IoT streaming platform handling 25,000 events/sec.',
        'Built a real-time event pipeline for connected vehicle telematics. Processed GPS, battery thermals, and fault detection codes with zero data drop during network partitioning. Provided interactive operations dashboards with real-time alerts.',
        'Python, Kafka, TimescaleDB, Redis, Go, Grafana, React',
        'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1000&q=80',
        'https://example.com/apex-telemetry',
        'https://github.com/example/apex-telemetry',
        true,
        2
    ),
    (
        'CloudMorph: Automated Multi-Cloud Infrastructure Synthesizer',
        'Declarative infrastructure compiler translating intent into hardened Terraform configs.',
        'Developer tool designed to accelerate cloud infrastructure provisioning. Generates audited, SOC2-compliant AWS and GCP infrastructure code with built-in cost projections, drift alerts, and automated security scanning.',
        'Python, Rust, Terraform, AWS CDK, Next.js, PostgreSQL',
        'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1000&q=80',
        'https://example.com/cloudmorph',
        'https://github.com/example/cloudmorph',
        false,
        3
    );

INSERT INTO certifications (title, issuer, issue_date, credential_url, media_url, media_type, display_order)
VALUES
    (
        'AWS Certified Solutions Architect - Professional',
        'Amazon Web Services (AWS)',
        'November 2025',
        'https://aws.amazon.com/certification/',
        'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=800&q=80',
        'image',
        1
    ),
    (
        'TensorFlow Developer Certificate',
        'Google',
        'March 2025',
        'https://www.tensorflow.org/certificate',
        'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=800&q=80',
        'image',
        2
    ),
    (
        'Certified Kubernetes Administrator (CKA)',
        'Cloud Native Computing Foundation (CNCF)',
        'July 2024',
        'https://www.cncf.io/certification/cka/',
        'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80',
        'image',
        3
    );
