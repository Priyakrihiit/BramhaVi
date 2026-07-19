/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { Organization, OrgInvitation, OrgRoster, OrgType } from './types';
import { Building2, Users2, ShieldAlert, Plus, Send, Network, GraduationCap, CheckCircle } from 'lucide-react';

export const Module2Organizations: React.FC = () => {
  const { currentUser } = useAuthStore();
  const [orgs, setOrgs] = useState<Organization[]>([
    {
      id: 'org-bvg-univ',
      name: 'BrahmaVidya University Pune',
      type: 'UNIVERSITY',
      domain: 'brahmavidya.edu',
      ownerId: 'user-admin',
      createdAt: '2026-01-01',
      departments: ['Computer Science', 'Data Analytics', 'Astrophysics', 'Vedic Mathematics'],
      employeeCount: 45,
      teacherCount: 120,
      studentCount: 3500
    }
  ]);

  const [selectedOrgId, setSelectedOrgId] = useState<string>('org-bvg-univ');

  const [invitations, setInvitations] = useState<OrgInvitation[]>([
    {
      id: 'inv-1',
      orgId: 'org-bvg-univ',
      email: 'prof.sharma@brahmavidya.edu',
      role: 'TEACHER',
      department: 'Vedic Mathematics',
      status: 'PENDING',
      createdAt: '2026-07-06'
    },
    {
      id: 'inv-2',
      orgId: 'org-bvg-univ',
      email: 'coordinator@brahmavidya.edu',
      role: 'ADMIN',
      department: 'Astrophysics',
      status: 'ACCEPTED',
      createdAt: '2026-07-05'
    }
  ]);

  const [roster, setRoster] = useState<OrgRoster[]>([
    {
      id: 'rost-1',
      orgId: 'org-bvg-univ',
      userId: 'user-teacher',
      fullName: 'Dr. Ananya Iyer',
      email: 'teacher@brahmavidya.edu',
      role: 'TEACHER',
      department: 'Computer Science',
      joinedAt: '2026-02-15'
    },
    {
      id: 'rost-2',
      orgId: 'org-bvg-univ',
      userId: 'user-student',
      fullName: 'Rahul Sharma',
      email: 'student@brahmavidya.edu',
      role: 'MEMBER',
      department: 'Vedic Mathematics',
      joinedAt: '2026-03-10'
    }
  ]);

  // Form states
  const [newOrgName, setNewOrgName] = useState('');
  const [newOrgType, setNewOrgType] = useState<OrgType>('SCHOOL');
  const [newOrgDomain, setNewOrgDomain] = useState('');
  
  const [newDeptName, setNewDeptName] = useState('');
  
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<'ADMIN' | 'TEACHER' | 'EMPLOYEE' | 'MEMBER'>('TEACHER');
  const [inviteDept, setInviteDept] = useState('Computer Science');

  const activeOrg = orgs.find(o => o.id === selectedOrgId);

  const handleCreateOrg = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newOrgName || !newOrgDomain) return;

    const newOrg: Organization = {
      id: `org-${Date.now()}`,
      name: newOrgName,
      type: newOrgType,
      domain: newOrgDomain.toLowerCase(),
      ownerId: currentUser?.id || 'user',
      createdAt: new Date().toISOString().split('T')[0],
      departments: ['Administration', 'General'],
      employeeCount: 1,
      teacherCount: 0,
      studentCount: 0
    };

    setOrgs(prev => [...prev, newOrg]);
    setSelectedOrgId(newOrg.id);
    setNewOrgName('');
    setNewOrgDomain('');
  };

  const handleAddDepartment = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDeptName || !activeOrg) return;

    setOrgs(prev => prev.map(o => {
      if (o.id === activeOrg.id) {
        if (o.departments.includes(newDeptName)) return o;
        return {
          ...o,
          departments: [...o.departments, newDeptName]
        };
      }
      return o;
    }));
    setNewDeptName('');
  };

  const handleSendInvite = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteEmail || !activeOrg) return;

    const newInvite: OrgInvitation = {
      id: `inv-${Date.now()}`,
      orgId: activeOrg.id,
      email: inviteEmail.toLowerCase(),
      role: inviteRole,
      department: inviteDept,
      status: 'PENDING',
      createdAt: new Date().toISOString().split('T')[0]
    };

    setInvitations(prev => [newInvite, ...prev]);
    setInviteEmail('');
  };

  return (
    <div id="saas-module-2" className="space-y-6 text-slate-100">
      {/* Page Header Banner */}
      <div className="bg-slate-900/60 border border-indigo-950 p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 text-left">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Building2 className="text-indigo-400 w-5 h-5" />
            Enterprise Organization & Multi-Tenant Management
          </h2>
          <p className="text-slate-400 text-xs mt-1">
            Manage educational ecosystems like Universities, Schools, Coaching Centers, and Corporate Groups. Maintain separate rosters, departments, user roles, and dispatch branded email invitations.
          </p>
        </div>
        <div className="flex gap-2">
          <select
            value={selectedOrgId}
            onChange={(e) => setSelectedOrgId(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-slate-200 text-xs rounded-xl px-4 py-2 font-semibold focus:outline-none focus:border-indigo-500"
          >
            {orgs.map(org => (
              <option key={org.id} value={org.id}>{org.name}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Panel: Register New Org & Active Org Status Counters */}
        <div className="space-y-6 lg:col-span-1">
          {/* Active Org Metadata Cards */}
          {activeOrg && (
            <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 space-y-4 text-left">
              <span className="text-[10px] bg-indigo-500/10 text-indigo-400 font-bold px-2 py-0.5 rounded-md uppercase tracking-wider">
                {activeOrg.type} Portal
              </span>
              <h3 className="text-base font-black text-white">{activeOrg.name}</h3>
              <p className="text-xs text-slate-400">Authorized Mail Domain: <strong className="text-indigo-300 font-mono">@{activeOrg.domain}</strong></p>

              <hr className="border-slate-900" />

              <div className="grid grid-cols-3 gap-2 text-center">
                <div className="bg-slate-900/40 border border-slate-850 p-2.5 rounded-xl">
                  <span className="block text-slate-500 text-[9px] uppercase font-bold">Teachers</span>
                  <span className="text-sm font-black text-white font-mono">{activeOrg.teacherCount || roster.filter(r => r.role === 'TEACHER').length}</span>
                </div>
                <div className="bg-slate-900/40 border border-slate-850 p-2.5 rounded-xl">
                  <span className="block text-slate-500 text-[9px] uppercase font-bold">Employees</span>
                  <span className="text-sm font-black text-white font-mono">{activeOrg.employeeCount}</span>
                </div>
                <div className="bg-slate-900/40 border border-slate-850 p-2.5 rounded-xl">
                  <span className="block text-slate-500 text-[9px] uppercase font-bold">Students</span>
                  <span className="text-sm font-black text-white font-mono">{activeOrg.studentCount || roster.filter(r => r.role === 'MEMBER').length}</span>
                </div>
              </div>
            </div>
          )}

          {/* Create New Org Form */}
          <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 text-left">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
              <Plus className="w-4 h-4 text-indigo-400" />
              Register New Organization
            </h3>
            <form onSubmit={handleCreateOrg} className="space-y-4">
              <div>
                <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Organization Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Stanford Academy"
                  value={newOrgName}
                  onChange={(e) => setNewOrgName(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Type</label>
                  <select
                    value={newOrgType}
                    onChange={(e) => setNewOrgType(e.target.value as OrgType)}
                    className="w-full bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="SCHOOL">School</option>
                    <option value="COLLEGE">College</option>
                    <option value="UNIVERSITY">University</option>
                    <option value="COACHING">Coaching</option>
                    <option value="COMPANY">Company</option>
                    <option value="NGO">NGO</option>
                    <option value="INSTITUTE">Institute</option>
                  </select>
                </div>
                <div>
                  <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Domain</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. stanford.edu"
                    value={newOrgDomain}
                    onChange={(e) => setNewOrgDomain(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold py-2 rounded-xl transition shadow-md shadow-indigo-950"
              >
                Create Enterprise Tenant
              </button>
            </form>
          </div>
        </div>

        {/* Center Panel: Department Building & Invitations */}
        <div className="space-y-6 lg:col-span-2">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Departments Manager */}
            <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 text-left flex flex-col justify-between">
              <div>
                <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
                  <Network className="w-4 h-4 text-indigo-400" />
                  Departments Matrix
                </h3>
                {activeOrg && (
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {activeOrg.departments.map((dept, idx) => (
                      <span key={idx} className="bg-slate-900 border border-slate-800 text-slate-300 text-[10px] px-2.5 py-1 rounded-lg">
                        {dept}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              <form onSubmit={handleAddDepartment} className="flex gap-2">
                <input
                  type="text"
                  required
                  placeholder="New Department..."
                  value={newDeptName}
                  onChange={(e) => setNewDeptName(e.target.value)}
                  className="flex-1 bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500"
                />
                <button type="submit" className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs px-3 py-1 rounded-lg transition font-bold">
                  Add
                </button>
              </form>
            </div>

            {/* Invite Members Form */}
            <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 text-left">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
                <Send className="w-4 h-4 text-indigo-400" />
                Invite Roster Member
              </h3>
              <form onSubmit={handleSendInvite} className="space-y-3">
                <input
                  type="email"
                  required
                  placeholder="Enter colleague's email address..."
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500"
                />
                <div className="grid grid-cols-2 gap-2">
                  <select
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value as any)}
                    className="bg-slate-900 border border-slate-850 rounded-lg px-2 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="TEACHER">Teacher</option>
                    <option value="ADMIN">Org Admin</option>
                    <option value="EMPLOYEE">Employee</option>
                    <option value="MEMBER">Student</option>
                  </select>
                  <select
                    value={inviteDept}
                    onChange={(e) => setInviteDept(e.target.value)}
                    className="bg-slate-900 border border-slate-850 rounded-lg px-2 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
                  >
                    {activeOrg?.departments.map((dept, i) => (
                      <option key={i} value={dept}>{dept}</option>
                    ))}
                  </select>
                </div>
                <button
                  type="submit"
                  className="w-full bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold py-1.5 rounded-xl transition flex items-center justify-center gap-1.5"
                >
                  <Send className="w-3.5 h-3.5" /> Dispatch Verification Invite
                </button>
              </form>
            </div>
          </div>

          {/* Combined Roster Table & Invitations log */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
            {/* Roster Table */}
            <div className="md:col-span-7 bg-slate-950/40 border border-slate-900 rounded-2xl p-5 text-left">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-3 flex items-center gap-2">
                <Users2 className="w-4 h-4 text-indigo-400" />
                Active Tenant Roster
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-xs font-mono">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-500">
                      <th className="pb-2 font-bold text-left">Member</th>
                      <th className="pb-2 font-bold text-left">Role</th>
                      <th className="pb-2 font-bold text-left">Dept</th>
                    </tr>
                  </thead>
                  <tbody>
                    {roster.map(rost => (
                      <tr key={rost.id} className="border-b border-slate-900/50">
                        <td className="py-2.5">
                          <span className="block font-sans font-bold text-slate-200 text-xs">{rost.fullName}</span>
                          <span className="block text-[10px] text-slate-500">{rost.email}</span>
                        </td>
                        <td className="py-2.5">
                          <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded-full ${rost.role === 'ADMIN' ? 'bg-indigo-500/10 text-indigo-400' : rost.role === 'TEACHER' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-800 text-slate-400'}`}>
                            {rost.role}
                          </span>
                        </td>
                        <td className="py-2.5 text-slate-400">{rost.department}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Invitations Ledger */}
            <div className="md:col-span-5 bg-slate-950/40 border border-slate-900 rounded-2xl p-5 text-left">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-3 flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-indigo-400" />
                Dispatched Invites Log
              </h3>
              <div className="space-y-2">
                {invitations.map(inv => (
                  <div key={inv.id} className="bg-slate-900/40 border border-slate-850 p-2.5 rounded-xl flex items-center justify-between">
                    <div className="text-left font-mono">
                      <span className="block text-slate-300 text-xs truncate max-w-[150px] font-sans font-semibold">{inv.email}</span>
                      <span className="block text-[9px] text-slate-500 mt-0.5">{inv.role} • {inv.department}</span>
                    </div>
                    <div>
                      {inv.status === 'PENDING' ? (
                        <span className="text-[9px] bg-amber-500/10 text-amber-400 px-2 py-0.5 rounded-full font-bold">PENDING</span>
                      ) : (
                        <span className="text-[9px] bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded-full font-bold flex items-center gap-0.5">
                          <CheckCircle className="w-2.5 h-2.5" /> OK
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Module2Organizations;
