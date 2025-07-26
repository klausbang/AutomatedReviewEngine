"""
Performance Monitor Component - Automated Review Engine

This module provides real-time performance monitoring for the UI application.
Phase 4.1 Day 3: Performance Optimization & Polish

Features:
- Real-time performance metrics
- Memory usage tracking
- Component render time monitoring
- Cache status display
- Performance recommendations
"""

import streamlit as st
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


class PerformanceMonitor:
    """Performance monitoring dashboard component"""
    
    def __init__(self):
        """Initialize performance monitor"""
        self.metrics_history = []
        self.performance_thresholds = {
            'render_time_warning': 2.0,  # seconds
            'render_time_critical': 5.0,  # seconds
            'memory_warning': 100,  # MB
            'memory_critical': 200,  # MB
            'cache_timeout': 300  # seconds
        }
    
    def render_performance_dashboard(self, show_details: bool = False):
        """Render the performance monitoring dashboard"""
        if not show_details:
            self._render_compact_view()
        else:
            self._render_detailed_view()
    
    def _render_compact_view(self):
        """Render compact performance view in sidebar"""
        with st.expander("📊 Performance", expanded=False):
            metrics = self._get_current_metrics()
            
            col1, col2 = st.columns(2)
            
            with col1:
                status = self._get_performance_status(metrics)
                if status == "good":
                    st.success("✅ Good")
                elif status == "warning":
                    st.warning("⚠️ Fair")
                else:
                    st.error("❌ Poor")
            
            with col2:
                if metrics.get('render_time'):
                    st.metric(
                        "Render Time",
                        f"{metrics['render_time']:.2f}s",
                        delta=self._get_render_time_delta()
                    )
    
    def _render_detailed_view(self):
        """Render detailed performance monitoring dashboard"""
        st.markdown("## 📊 Performance Monitor")
        
        # Current metrics overview
        self._render_metrics_overview()
        
        # Performance charts
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_render_time_chart()
        
        with col2:
            self._render_memory_usage_chart()
        
        # Component performance breakdown
        self._render_component_performance()
        
        # Cache status
        self._render_cache_status()
        
        # Performance recommendations
        self._render_recommendations()
    
    def _render_metrics_overview(self):
        """Render current metrics overview"""
        metrics = self._get_current_metrics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            render_time = metrics.get('render_time', 0)
            delta_color = "normal"
            if render_time > self.performance_thresholds['render_time_critical']:
                delta_color = "inverse"
            elif render_time > self.performance_thresholds['render_time_warning']:
                delta_color = "off"
            
            st.metric(
                "🕒 Render Time",
                f"{render_time:.2f}s",
                delta=self._get_render_time_delta(),
                delta_color=delta_color
            )
        
        with col2:
            memory_usage = metrics.get('memory_usage', 0)
            delta_color = "normal"
            if memory_usage > self.performance_thresholds['memory_critical']:
                delta_color = "inverse"
            elif memory_usage > self.performance_thresholds['memory_warning']:
                delta_color = "off"
            
            st.metric(
                "💾 Memory Usage",
                f"{memory_usage:.1f} MB",
                delta=self._get_memory_delta(),
                delta_color=delta_color
            )
        
        with col3:
            cache_status = self._get_cache_status()
            cache_health = "🟢 Active" if cache_status['active'] else "🔴 Inactive"
            st.metric(
                "🗄️ Cache Status",
                cache_health,
                delta=f"{cache_status['hit_rate']:.1f}% hit rate"
            )
        
        with col4:
            component_count = len(st.session_state.get('performance_metrics', {}))
            st.metric(
                "🧩 Active Components",
                f"{component_count}",
                delta=None
            )
    
    def _render_render_time_chart(self):
        """Render render time performance chart"""
        st.markdown("### ⏱️ Render Time Trends")
        
        performance_data = st.session_state.get('app_performance', [])
        
        if not performance_data:
            st.info("No performance data available yet")
            return
        
        # Prepare data
        timestamps = [entry['timestamp'] for entry in performance_data[-20:]]
        render_times = [entry['render_time'] for entry in performance_data[-20:]]
        
        # Create chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=render_times,
            mode='lines+markers',
            name='Render Time',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=6)
        ))
        
        # Add threshold lines
        fig.add_hline(
            y=self.performance_thresholds['render_time_warning'],
            line_dash="dash",
            line_color="orange",
            annotation_text="Warning Threshold"
        )
        
        fig.add_hline(
            y=self.performance_thresholds['render_time_critical'],
            line_dash="dash",
            line_color="red",
            annotation_text="Critical Threshold"
        )
        
        fig.update_layout(
            height=300,
            xaxis_title="Time",
            yaxis_title="Render Time (seconds)",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_memory_usage_chart(self):
        """Render memory usage chart"""
        st.markdown("### 💾 Memory Usage Trends")
        
        performance_data = st.session_state.get('app_performance', [])
        
        if not performance_data:
            st.info("No memory data available yet")
            return
        
        # Prepare data
        timestamps = [entry['timestamp'] for entry in performance_data[-20:]]
        memory_usage = [entry.get('memory_usage', 0) for entry in performance_data[-20:]]
        
        # Create chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=memory_usage,
            mode='lines+markers',
            name='Memory Usage',
            fill='tonexty',
            line=dict(color='#2ca02c', width=2),
            marker=dict(size=6)
        ))
        
        # Add threshold lines
        fig.add_hline(
            y=self.performance_thresholds['memory_warning'],
            line_dash="dash",
            line_color="orange",
            annotation_text="Warning Threshold"
        )
        
        fig.add_hline(
            y=self.performance_thresholds['memory_critical'],
            line_dash="dash",
            line_color="red",
            annotation_text="Critical Threshold"
        )
        
        fig.update_layout(
            height=300,
            xaxis_title="Time",
            yaxis_title="Memory Usage (MB)",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_component_performance(self):
        """Render component-specific performance metrics"""
        st.markdown("### 🧩 Component Performance")
        
        component_metrics = st.session_state.get('performance_metrics', {})
        
        if not component_metrics:
            st.info("No component performance data available")
            return
        
        # Create performance summary table
        performance_data = []
        for component, execution_time in component_metrics.items():
            status = "🟢 Good"
            if execution_time > 2.0:
                status = "🔴 Slow"
            elif execution_time > 1.0:
                status = "🟡 Fair"
            
            performance_data.append({
                'Component': component,
                'Execution Time': f"{execution_time:.3f}s",
                'Status': status,
                'Optimization': self._get_optimization_suggestion(component, execution_time)
            })
        
        if performance_data:
            import pandas as pd
            df = pd.DataFrame(performance_data)
            st.dataframe(df, use_container_width=True)
    
    def _render_cache_status(self):
        """Render cache status information"""
        st.markdown("### 🗄️ Cache Management")
        
        cache_info = self._get_cache_status()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Cache Status:** {'🟢 Active' if cache_info['active'] else '🔴 Inactive'}")
        
        with col2:
            st.info(f"**Hit Rate:** {cache_info['hit_rate']:.1f}%")
        
        with col3:
            last_clear = cache_info.get('last_clear', 'Never')
            if isinstance(last_clear, datetime):
                last_clear = last_clear.strftime('%H:%M:%S')
            st.info(f"**Last Clear:** {last_clear}")
        
        # Cache management controls
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Cache", help="Clear component cache to free memory"):
                self._clear_cache()
                st.success("Cache cleared successfully")
                st.rerun()
        
        with col2:
            if st.button("📊 Refresh Metrics", help="Refresh performance metrics"):
                st.rerun()
    
    def _render_recommendations(self):
        """Render performance optimization recommendations"""
        st.markdown("### 💡 Performance Recommendations")
        
        recommendations = self._get_performance_recommendations()
        
        if not recommendations:
            st.success("✅ No performance issues detected")
            return
        
        for rec in recommendations:
            if rec['severity'] == 'critical':
                st.error(f"🚨 **Critical:** {rec['message']}")
            elif rec['severity'] == 'warning':
                st.warning(f"⚠️ **Warning:** {rec['message']}")
            else:
                st.info(f"💡 **Suggestion:** {rec['message']}")
    
    def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        performance_data = st.session_state.get('app_performance', [])
        
        if not performance_data:
            return {}
        
        latest = performance_data[-1]
        return {
            'render_time': latest.get('render_time', 0),
            'memory_usage': latest.get('memory_usage', 0),
            'timestamp': latest.get('timestamp')
        }
    
    def _get_performance_status(self, metrics: Dict[str, Any]) -> str:
        """Determine overall performance status"""
        render_time = metrics.get('render_time', 0)
        memory_usage = metrics.get('memory_usage', 0)
        
        if (render_time > self.performance_thresholds['render_time_critical'] or 
            memory_usage > self.performance_thresholds['memory_critical']):
            return "critical"
        elif (render_time > self.performance_thresholds['render_time_warning'] or 
              memory_usage > self.performance_thresholds['memory_warning']):
            return "warning"
        else:
            return "good"
    
    def _get_render_time_delta(self) -> Optional[str]:
        """Calculate render time delta"""
        performance_data = st.session_state.get('app_performance', [])
        
        if len(performance_data) < 2:
            return None
        
        current = performance_data[-1]['render_time']
        previous = performance_data[-2]['render_time']
        delta = current - previous
        
        return f"{delta:+.2f}s"
    
    def _get_memory_delta(self) -> Optional[str]:
        """Calculate memory usage delta"""
        performance_data = st.session_state.get('app_performance', [])
        
        if len(performance_data) < 2:
            return None
        
        current = performance_data[-1].get('memory_usage', 0)
        previous = performance_data[-2].get('memory_usage', 0)
        delta = current - previous
        
        return f"{delta:+.1f} MB"
    
    def _get_cache_status(self) -> Dict[str, Any]:
        """Get cache status information"""
        cache_status = st.session_state.get('cache_status', 'inactive')
        
        # Simulate cache metrics
        return {
            'active': cache_status == 'active',
            'hit_rate': 85.0,  # Would be calculated from actual cache hits
            'last_clear': st.session_state.get('last_cache_clear')
        }
    
    def _get_optimization_suggestion(self, component: str, execution_time: float) -> str:
        """Get optimization suggestion for component"""
        if execution_time > 2.0:
            return "Consider lazy loading or caching"
        elif execution_time > 1.0:
            return "Monitor for optimization opportunities"
        else:
            return "Performance acceptable"
    
    def _get_performance_recommendations(self) -> List[Dict[str, str]]:
        """Generate performance recommendations"""
        recommendations = []
        metrics = self._get_current_metrics()
        
        # Check render time
        render_time = metrics.get('render_time', 0)
        if render_time > self.performance_thresholds['render_time_critical']:
            recommendations.append({
                'severity': 'critical',
                'message': f"Render time ({render_time:.2f}s) exceeds critical threshold. Consider component optimization."
            })
        elif render_time > self.performance_thresholds['render_time_warning']:
            recommendations.append({
                'severity': 'warning',
                'message': f"Render time ({render_time:.2f}s) above optimal range. Monitor performance."
            })
        
        # Check memory usage
        memory_usage = metrics.get('memory_usage', 0)
        if memory_usage > self.performance_thresholds['memory_critical']:
            recommendations.append({
                'severity': 'critical',
                'message': f"Memory usage ({memory_usage:.1f} MB) is very high. Clear cache or restart session."
            })
        elif memory_usage > self.performance_thresholds['memory_warning']:
            recommendations.append({
                'severity': 'warning',
                'message': f"Memory usage ({memory_usage:.1f} MB) is elevated. Consider cache management."
            })
        
        # Check component performance
        component_metrics = st.session_state.get('performance_metrics', {})
        slow_components = [name for name, time in component_metrics.items() if time > 2.0]
        
        if slow_components:
            recommendations.append({
                'severity': 'warning',
                'message': f"Slow components detected: {', '.join(slow_components)}. Consider optimization."
            })
        
        return recommendations
    
    def _clear_cache(self):
        """Clear application cache"""
        # Clear Streamlit cache
        if hasattr(st, 'cache_resource'):
            st.cache_resource.clear()
        
        # Update session state
        st.session_state.cache_status = 'cleared'
        st.session_state.last_cache_clear = datetime.now()
        
        # Clear performance metrics
        if 'performance_metrics' in st.session_state:
            st.session_state.performance_metrics.clear()


def create_performance_monitor():
    """Factory function to create performance monitor component"""
    return PerformanceMonitor()
