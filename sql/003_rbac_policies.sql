-- ========================================================
-- 1. Audit Logs Policies
-- ========================================================
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Admin Role ရှိသူများသာ audit_logs ကို ကြည့်ရှုခွင့်ပေးခြင်း
CREATE POLICY "Admin can view audit logs" ON audit_logs
FOR SELECT
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM user_roles ur
    JOIN roles r ON ur.role_id = r.id
    WHERE ur.user_id = auth.uid() AND r.name = 'Admin'
  )
);

-- Audit logs အား မည်သူမျှ ပြင်ဆင်/ဖျက်ဆီး၍မရအောင် တားဆီးခြင်း
CREATE POLICY "No one can modify audit logs" ON audit_logs
FOR INSERT WITH CHECK (false);


-- ========================================================
-- 2. Roles & Permissions Read Policies
-- ========================================================
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;

-- Login ဝင်ထားသော User တိုင်း Role name များကို ဖတ်ရှုခွင့်ပေးခြင်း
CREATE POLICY "Allow public read-only for roles" ON roles 
FOR SELECT TO authenticated USING (true);

ALTER TABLE permissions ENABLE ROW LEVEL SECURITY;

-- Login ဝင်ထားသော User တိုင်း Permission name များကို ဖတ်ရှုခွင့်ပေးခြင်း
CREATE POLICY "Allow public read-only for permissions" ON permissions 
FOR SELECT TO authenticated USING (true);
