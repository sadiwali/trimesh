try:
    from . import generic as g
except BaseException:
    import generic as g


class PlyTest(g.unittest.TestCase):

    def test_ply_dtype(self):
        # make sure all ply dtype strings are valid dtypes
        dtypes = g.trimesh.exchange.ply.dtypes
        for d in dtypes.values():
            # will raise if dtype string not valid
            g.np.dtype(d)

    def test_ply(self):
        m = g.get_mesh('machinist.XAML')

        assert m.visual.kind == 'face'
        assert m.visual.face_colors.ptp(axis=0).max() > 0

        export = m.export(file_type='ply')
        reconstructed = g.wrapload(export, file_type='ply')

        assert reconstructed.visual.kind == 'face'

        assert g.np.allclose(reconstructed.visual.face_colors,
                             m.visual.face_colors)

        m = g.get_mesh('reference.ply')

        assert m.visual.kind == 'vertex'
        assert m.visual.vertex_colors.ptp(axis=0).max() > 0

        export = m.export(file_type='ply')
        reconstructed = g.wrapload(export, file_type='ply')
        assert reconstructed.visual.kind == 'vertex'

        assert g.np.allclose(reconstructed.visual.vertex_colors,
                             m.visual.vertex_colors)

    def test_points(self):
        # Test reading point clouds from PLY files

        m = g.get_mesh('points_ascii.ply')
        assert isinstance(m, g.trimesh.PointCloud)
        assert m.vertices.shape == (5, 3)

        m = g.get_mesh('points_bin.ply')
        assert m.vertices.shape == (5, 3)
        assert isinstance(m, g.trimesh.PointCloud)

        m = g.get_mesh('points_emptyface.ply')
        assert m.vertices.shape == (1024, 3)
        assert isinstance(m, g.trimesh.PointCloud)

    def test_list_properties(self):
        """
        Test reading point clouds with the following metadata:
        - lists of differing length
        - multiple list properties
        - single-element properties that come after list properties
        """
        m = g.get_mesh('points_ascii_with_lists.ply')

        point_list = m.metadata['ply_raw']['point_list']['data']
        assert g.np.array_equal(
            point_list['point_indices1'][0], g.np.array([10, 11, 12], dtype=g.np.uint32))
        assert g.np.array_equal(
            point_list['point_indices1'][1], g.np.array([10, 11], dtype=g.np.uint32))
        assert g.np.array_equal(
            point_list['point_indices2'][0], g.np.array([13, 14], dtype=g.np.uint32))
        assert g.np.array_equal(
            point_list['point_indices2'][1], g.np.array([12, 13, 14], dtype=g.np.uint32))
        assert g.np.array_equal(
            point_list['some_float'], g.np.array([1.1, 2.2], dtype=g.np.float32))

    def test_vertex_attributes(self):
        """
        Test writing vertex attributes to a ply, by reading them back and asserting the
        written attributes array matches
        """

        m = g.get_mesh('box.STL')
        test_1d_attribute = g.np.copy(m.vertices[:, 0])
        test_nd_attribute = g.np.copy(m.vertices)
        m.vertex_attributes['test_1d_attribute'] = test_1d_attribute
        m.vertex_attributes['test_nd_attribute'] = test_nd_attribute

        export = m.export(file_type='ply')
        reconstructed = g.wrapload(export,
                                   file_type='ply')

        vertex_attributes = reconstructed.metadata['ply_raw']['vertex']['data']
        result_1d = vertex_attributes['test_1d_attribute']
        result_nd = vertex_attributes['test_nd_attribute']['f1']

        g.np.testing.assert_almost_equal(result_1d, test_1d_attribute)
        g.np.testing.assert_almost_equal(result_nd, test_nd_attribute)

    def test_face_attributes(self):
        # Test writing face attributes to a ply, by reading
        # them back and asserting the written attributes array matches

        m = g.get_mesh('box.STL')
        test_1d_attribute = g.np.copy(m.face_angles[:, 0])
        test_nd_attribute = g.np.copy(m.face_angles)
        m.face_attributes['test_1d_attribute'] = test_1d_attribute
        m.face_attributes['test_nd_attribute'] = test_nd_attribute

        export = m.export(file_type='ply')
        reconstructed = g.wrapload(export, file_type='ply')

        face_attributes = reconstructed.metadata['ply_raw']['face']['data']
        result_1d = face_attributes['test_1d_attribute']
        result_nd = face_attributes['test_nd_attribute']['f1']

        g.np.testing.assert_almost_equal(result_1d, test_1d_attribute)
        g.np.testing.assert_almost_equal(result_nd, test_nd_attribute)

        no_attr = m.export(file_type='ply', include_attributes=False)
        assert len(no_attr) < len(export)

    def test_cases(self):
        a = g.get_mesh('featuretype.STL')
        b = g.get_mesh('featuretype.ply')
        assert a.faces.shape == b.faces.shape

        # has mixed quads and triangles
        m = g.get_mesh('suzanne.ply')
        assert len(m.faces) > 0

    def test_ascii_color(self):
        mesh = g.trimesh.creation.box()
        en = g.wrapload(mesh.export(file_type='ply', encoding="ascii"),
                        file_type='ply')
        assert en.visual.kind is None

        color = [255, 0, 0, 255]
        mesh.visual.vertex_colors = color

        # try exporting and reloading raw
        eb = g.wrapload(mesh.export(file_type='ply'), file_type='ply')

        assert g.np.allclose(eb.visual.vertex_colors[0], color)
        assert eb.visual.kind == 'vertex'

        ea = g.wrapload(mesh.export(file_type='ply', encoding='ascii'),
                        file_type='ply')
        assert g.np.allclose(ea.visual.vertex_colors, color)
        assert ea.visual.kind == 'vertex'


if __name__ == '__main__':
    g.trimesh.util.attach_to_log()
    g.unittest.main()
