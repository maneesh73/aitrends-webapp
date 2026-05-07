import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'

export function usePaginatedFetch(baseUrl, params = {}) {
  const [data, setData] = useState({ items: [], total: 0, has_next: false })
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await axios.get(baseUrl, { params: { page, page_size: 12, ...params } })
      setData(res.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [baseUrl, page, JSON.stringify(params)])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  useEffect(() => {
    setPage(1)
  }, [JSON.stringify(params)])

  return { data, page, setPage, loading, error, refetch: fetchData }
}
