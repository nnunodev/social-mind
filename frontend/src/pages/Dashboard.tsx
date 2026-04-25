import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Upload, TrendingUp, Users, Heart, Share2 } from 'lucide-react';
import api from '../services/api';

interface AnalyticsSummary {
  total_views: number;
  total_likes: number;
  total_comments: number;
  total_shares: number;
  avg_engagement_rate: number;
  top_performing_content: any[];
  growth_by_date: any[];
}

export default function Dashboard() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadPlatform, setUploadPlatform] = useState('youtube');

  useEffect(() => {
    fetchSummary();
  }, []);

  const fetchSummary = async () => {
    try {
      const response = await api.get('/analytics/summary');
      setSummary(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;

    const formData = new FormData();
    formData.append('file', uploadFile);

    try {
      await api.post(`/analytics/upload?platform=${uploadPlatform}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setUploadFile(null);
      fetchSummary();
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-500">Loading analytics...</div>
      </div>
    );
  }

  const stats = [
    { name: 'Total Views', value: summary?.total_views || 0, icon: TrendingUp, color: 'bg-blue-500' },
    { name: 'Total Likes', value: summary?.total_likes || 0, icon: Heart, color: 'bg-red-500' },
    { name: 'Total Comments', value: summary?.total_comments || 0, icon: Users, color: 'bg-green-500' },
    { name: 'Total Shares', value: summary?.total_shares || 0, icon: Share2, color: 'bg-purple-500' },
  ];

  const growthData = summary?.growth_by_date || [];

  return (
    <div className="space-y-6">
      <div className="sm:flex sm:items-center sm:justify-between">
        <h1 className="text-2xl font-semibold text-gray-900">Analytics Dashboard</h1>
      </div>

      {/* Upload Section */}
      <div className="card">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Upload Analytics CSV</h2>
        <form onSubmit={handleFileUpload} className="flex flex-wrap gap-4">
          <select
            value={uploadPlatform}
            onChange={(e) => setUploadPlatform(e.target.value)}
            className="input w-auto"
          >
            <option value="youtube">YouTube</option>
            <option value="instagram">Instagram</option>
            <option value="tiktok">TikTok</option>
            <option value="twitter">Twitter</option>
          </select>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
            className="input w-auto"
          />
          <button
            type="submit"
            disabled={!uploadFile}
            className="btn-primary disabled:opacity-50"
          >
            <Upload className="w-4 h-4 mr-2" />
            Upload
          </button>
        </form>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.name} className="card">
            <div className="flex items-center">
              <div className={`flex-shrink-0 rounded-md p-3 ${stat.color}`}>
                <stat.icon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">{stat.name}</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {stat.value.toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      {growthData.length > 0 && (
        <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
          {/* Growth Chart */}
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Growth Over Time</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={growthData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="views" stroke="#0ea5e9" />
                <Line type="monotone" dataKey="likes" stroke="#ef4444" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Engagement Chart */}
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Engagement Breakdown</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={[
                  { name: 'Likes', value: summary?.total_likes || 0 },
                  { name: 'Comments', value: summary?.total_comments || 0 },
                  { name: 'Shares', value: summary?.total_shares || 0 },
                ]}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#0ea5e9" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Top Performing Content */}
      {summary?.top_performing_content && summary.top_performing_content.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Top Performing Content</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Title
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Views
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Engagement Rate
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {summary.top_performing_content.map((content) => (
                  <tr key={content.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {content.title || 'Untitled'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {content.views.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {(content.engagement_rate * 100).toFixed(2)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
